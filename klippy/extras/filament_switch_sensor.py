# Generic Filament Sensor Module
#
# Copyright (C) 2019  Eric Callahan <arksine.code@gmail.com>
#
# This file may be distributed under the terms of the GNU GPLv3 license.
import logging

class BaseSensor(object):
    def __init__(self, config):
        self.name = config.get_name().split()[1]
        self.printer = config.get_printer()
        self.gcode = self.printer.lookup_object('gcode')
        self.runout_gcode = config.get('runout_gcode', None)
        self.insert_gcode = config.get('insert_gcode', None)
        self.runout_pause = config.getboolean('pause_on_runout', True)
        if self.runout_pause:
            if self.runout_gcode is None:
                self.runout_gcode = "PAUSE"
            else:
                self.runout_gcode = "PAUSE\n" + self.runout_gcode
        self.runout_enabled = False
        self.insert_enabled = self.insert_gcode is not None
        self.event_running = False
        self.print_status = "idle"
        self.printer.register_event_handler(
            "idle_timeout:idle",
            (lambda e, s=self, st="idle": s._update_print_status(e, st)))
        self.printer.register_event_handler(
            "idle_timeout:ready",
            (lambda e, s=self, st="ready": s._update_print_status(e, st)))
        self.printer.register_event_handler(
            "idle_timeout:printing",
            (lambda e, s=self, st="printing": s._update_print_status(e, st)))
    def _handle_ready(self):
        self.toolhead = self.printer.lookup_object('toolhead')
    def _update_print_status(self, eventtime, status):
        if status == "printing":
            runout_en = self.runout_gcode is not None
            self.set_enable(runout_en, False)
        else:
            insert_en = self.insert_gcode is not None
            self.set_enable(False, insert_en)
    def _runout_event_handler(self, eventtime):
        if self.event_running:
            return
        self.event_running = True
        # Pausing from inside an event requires that the pause portion
        # of pause_resume execute immediately.
        pause_resume = self.printer.lookup_object('pause_resume', None)
        if self.runout_pause and pause_resume is not None:
            pause_resume.send_pause_command()
        self._exec_gcode(self.runout_gcode)
        self.event_running = False
    def _insert_event_handler(self, eventtime):
        if self.event_running:
            return
        self.event_running = True
        self._exec_gcode(self.insert_gcode)
        self.event_running = False
    def _exec_gcode(self, script):
        try:
            self.gcode.run_script(script)
        except Exception:
            logging.exception("Script running error")
    def set_enable(self, runout, insert):
        if runout and insert:
            # both cannot be enabled
            insert = False
        self.runout_enabled = runout
        self.insert_enabled = insert
    cmd_QUERY_FILAMENT_SENSOR_help = "Query the status of the Filament Sensor"
    def cmd_QUERY_FILAMENT_SENSOR(self, params):
        raise NotImplementedError(
            "Sensor must implement cmd_QUERY_FILAMENT_SENSOR")

class SwitchSensor(BaseSensor):
    def __init__(self, config):
        super(SwitchSensor, self).__init__(config)
        self.reactor = self.printer.get_reactor()
        self.buttons = self.printer.try_load_module(config, 'buttons')
        switch_pin = config.get('switch_pin')
        self.buttons.register_buttons([switch_pin], self._button_handler)
        self.event_delay = config.getfloat('event_delay', 3., above=0.)
        self.start_time = self.reactor.NEVER
        self.last_button_state = False
        self.last_cb_event_time = 0.
        self.gcode.register_mux_command(
            "QUERY_FILAMENT_SENSOR", "SENSOR", self.name,
            self.cmd_QUERY_FILAMENT_SENSOR,
            desc=self.cmd_QUERY_FILAMENT_SENSOR_help)
        self.printer.register_event_handler("klippy:ready", self._handle_ready)
    def _handle_ready(self):
        super(SwitchSensor, self)._handle_ready()
        self.start_time = self.reactor.monotonic() + 2.
    def _button_handler(self, eventtime, state):
        if eventtime < self.start_time or state == self.last_button_state:
            self.last_button_state = state
            return
        if state:
            # button pushed, check if insert callback should happen
            if (self.insert_enabled and
                    (eventtime - self.last_cb_event_time) > self.event_delay):
                self.last_cb_event_time = eventtime
                logging.info(
                    "switch_sensor: insert event detected, Time %.2f",
                    eventtime)
                self.reactor.register_callback(self._insert_event_handler)
        elif (self.runout_enabled and
                (eventtime - self.last_cb_event_time) > self.event_delay):
            # Filament runout detected
            self.last_cb_event_time = eventtime
            logging.info(
                "switch_sensor: runout event detected, Time %.2f", eventtime)
            self.reactor.register_callback(self._runout_event_handler)
        self.last_button_state = state
    def cmd_QUERY_FILAMENT_SENSOR(self, params):
        if self.last_button_state:
            msg = "Switch Sensor: filament detected"
        else:
            msg = "Switch Sensor: filament not detected"
        self.gcode.respond_info(msg)

def load_config_prefix(config):
    return SwitchSensor(config)
