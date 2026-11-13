"""Automated checks for Lab 8: Thermometer.

Each class is checked on its own, on a pretend board, so a check passes or fails
on one file alone, whatever state the other files are in. The pretend temperature
sensor reports the raw numbers each check chooses. The program check runs main
with all four classes together and reads only the thermometer log at the end,
not the narrative lines. Log values forgive extra spaces, letter case, and a
missing colon.

Time passes only when the code calls sleep. When a check fails, the assertion
message says what came out wrong and what was expected. gatorgrade does not show
that message itself; it prints the pytest command to run.
"""

import importlib
import re
from unittest.mock import patch

import mockro
from machine import ADC, Pin

MODULES = ("sensor", "levels", "display", "log", "main")
# A raw reading of 14184 is about 72 degrees Fahrenheit
ROOM = 14184


def fahrenheit_of(raw):
    """The temperature the formulas in the README give for one raw reading."""
    voltage = raw * 3.3 / 65535
    return (27 - (voltage - 0.706) / 0.001721) * 9 / 5 + 32


def close(got, expected):
    try:
        return abs(float(got) - expected) < 0.01
    except (TypeError, ValueError):
        return False


class Board:
    """The pins of a pretend Pico, told apart by GP number.

    `raws` is the list of numbers the temperature sensor reports in turn.
    `presses` is a list of (start, end) times in seconds: the button reads 0 while
    the clock is inside one of them. `clock` adds up the time slept, and `sleeps`
    keeps which LEDs were lit during each one.
    """

    def __init__(self, raws=None, presses=None):
        self.raws = list(raws or [])
        self.presses = list(presses or [])
        self.clock = 0.0
        self.numbers = {}
        self.inputs = set()
        self.lit = {}
        self.sleeps = []
        self.adc_reads = 0

    def sleep(self, seconds=0, *rest):
        self.sleeps.append((seconds, sorted(number for number, on in self.lit.items() if on)))
        self.clock += seconds

    def number(self, pin):
        if id(pin) not in self.numbers:
            for args, _ in mockro.get_recorder().calls("machine.Pin.init"):
                if len(args) >= 3 and args[0] is pin:
                    self.numbers[id(pin)] = args[2]
                    if len(args) >= 4 and args[3] == Pin.IN:
                        self.inputs.add(args[2])
        return self.numbers.get(id(pin))

    def value(self, pin, *rest):
        # mockro passes the Pin twice, then the argument: (pin, pin, x)
        x = rest[-1] if rest and rest[-1] is not pin else None
        number = self.number(pin)
        if x is None:
            if number in self.inputs:
                return 0 if any(start <= self.clock < end for start, end in self.presses) else 1
            return int(self.lit.get(number, False))
        self.lit[number] = bool(x)
        return 0

    def on(self, pin, *rest):
        self.lit[self.number(pin)] = True

    def off(self, pin, *rest):
        self.lit[self.number(pin)] = False

    def read_u16(self, adc=None):
        self.adc_reads += 1
        return self.raws.pop(0) if self.raws else ROOM


def adc_channels():
    return [args[2] for args, _ in mockro.get_recorder().calls("machine.ADC.__init__") if len(args) >= 3]


def on_board(board, action):
    """Run `action()` with the pins and the sensor wired to `board` and sleep patched."""
    mockro.get_recorder().clear()
    stubs = [patch("time.sleep", side_effect=board.sleep), patch.object(ADC, "read_u16", board.read_u16)]
    for name in MODULES:
        try:
            module = importlib.import_module(name)
        except Exception:
            continue
        if hasattr(module, "sleep"):
            stubs.append(patch.object(module, "sleep", side_effect=board.sleep))
    try:
        with mockro.override(machine_Pin_value=board.value, machine_Pin_on=board.on, machine_Pin_off=board.off):
            for stub in stubs:
                stub.start()
            try:
                return action()
            finally:
                for stub in stubs:
                    stub.stop()
    except AssertionError:
        raise
    except Exception as exc:
        raise AssertionError(f"the code stopped with {type(exc).__name__}: {exc}") from None


def test_the_sensor_reads_a_voltage_and_counts_it():
    from sensor import Sensor

    board = Board(raws=[0, 65535, 14184])

    def action():
        sensor = Sensor()
        seen = [sensor.readings, adc_channels()]
        seen.append([sensor.read_voltage(), sensor.read_voltage(), sensor.read_voltage()])
        seen.append(sensor.readings)
        return seen

    start, channels, voltages, after = on_board(board, action)
    assert channels == [4], f"Sensor() made ADC objects on {channels}, expected one on channel 4: ADC(4)"
    assert start == 0, f"readings started at {start}, expected 0"
    for raw, got in zip((0, 65535, 14184), voltages):
        assert close(got, raw * 3.3 / 65535), (
            f"read_voltage() returned {got} when the sensor reported {raw}, expected {raw * 3.3 / 65535:.4f}: "
            f"the reading times 3.3, divided by 65535"
        )
    assert after == 3, f"after three calls to read_voltage(), readings was {after}, expected 3"


def test_the_sensor_converts_to_celsius_and_fahrenheit():
    from sensor import Sensor

    board = Board(raws=[14184, 13000, 15000])

    def action():
        sensor = Sensor()
        return sensor.read_celsius(), sensor.read_fahrenheit(), sensor.read_fahrenheit(), sensor.readings

    celsius, first, second, readings = on_board(board, action)
    want = (fahrenheit_of(14184) - 32) * 5 / 9
    assert close(celsius, want), (
        f"read_celsius() returned {celsius} for a raw reading of 14184, expected {want:.2f}: "
        f"27 minus (voltage minus 0.706) divided by 0.001721, with the voltage from self.read_voltage()"
    )
    for raw, got in ((13000, first), (15000, second)):
        assert close(got, fahrenheit_of(raw)), (
            f"read_fahrenheit() returned {got} for a raw reading of {raw}, expected {fahrenheit_of(raw):.2f}: "
            f"the Celsius temperature from self.read_celsius(), times 9, divided by 5, plus 32"
        )
    assert readings == 3, (
        f"three conversions left readings at {readings}, expected 3: each conversion reads the sensor once, "
        f"through read_voltage()"
    )


def test_the_levels_sort_a_temperature():
    from levels import Levels

    levels = Levels(70, 80)
    assert (levels.cold_below, levels.hot_above) == (70, 80), (
        f"Levels(70, 80) stored cold_below {levels.cold_below} and hot_above {levels.hot_above}, expected 70 and 80"
    )
    for fahrenheit, want in ((50, "cold"), (69.9, "cold"), (70, "warm"), (75, "warm"), (80, "warm"), (80.1, "hot"), (95, "hot")):
        got = levels.level(fahrenheit)
        assert got == want, (
            f"level({fahrenheit}) with Levels(70, 80) returned {got!r}, expected {want!r}: below cold_below is "
            f"cold, above hot_above is hot, and anything else, including the two dividing temperatures, is warm"
        )
    other = Levels(30, 40)
    assert other.level(35) == "warm" and other.level(75) == "hot", (
        "level() with Levels(30, 40) did not use those numbers: compare with self.cold_below and self.hot_above"
    )


def test_the_levels_describe_a_temperature():
    from levels import Levels

    levels = Levels(70, 80)
    for fahrenheit, want in ((65, False), (72, True), (85, False)):
        got = levels.is_comfortable(fahrenheit)
        assert got is want, f"is_comfortable({fahrenheit}) with Levels(70, 80) returned {got!r}, expected {want}"
    for fahrenheit, number, word in ((72.46, "72.5", "warm"), (85.04, "85.0", "hot"), (60.0, "60.0", "cold")):
        got = levels.describe(fahrenheit)
        assert isinstance(got, str), f"describe({fahrenheit}) returned {got!r}, expected a string"
        assert number in got and word in got.lower(), (
            f"describe({fahrenheit}) returned {got!r}, expected a string with {number} (the temperature "
            f"rounded to one decimal place) and the level {word!r}"
        )


def test_the_display_starts_dark_with_its_lights_in_a_dictionary():
    from display import Display

    board = Board()

    def action():
        display = Display(15, 14, 13)
        start = (dict(board.lit), display.showing)
        display.lights["warm"].on()
        display.showing = "warm"
        display.all_off()
        return display, start, (dict(board.lit), display.showing)

    display, (lit, showing), (after_lit, after_showing) = on_board(board, action)
    lights = getattr(display, "lights", None)
    assert isinstance(lights, dict) and sorted(lights) == ["cold", "hot", "warm"], (
        f"Display has lights {lights!r}, expected a dictionary with the keys hot, warm and cold"
    )
    pins = {level: board.number(lights[level]) for level in lights}
    assert pins == {"hot": 15, "warm": 14, "cold": 13}, (
        f"Display(15, 14, 13) put the levels on {pins}, expected hot on GP15, warm on GP14 and cold on GP13"
    )
    assert not any(lit.get(number) for number in (13, 14, 15)) and showing == "off", (
        f"after Display(15, 14, 13), showing was {showing!r}, expected 'off', with the three LEDs off"
    )
    assert not any(after_lit.get(number) for number in (13, 14, 15)) and after_showing == "off", (
        f"after all_off(), showing was {after_showing!r} and the LEDs on were "
        f"{[n for n in (13, 14, 15) if after_lit.get(n)]}, expected 'off' and none"
    )


def test_the_display_shows_one_level_and_tests_its_lights():
    from display import Display

    board = Board()

    def action():
        display = Display(15, 14, 13)
        seen = []
        for level in ("hot", "cold", "warm"):
            display.show(level)
            seen.append((level, display.showing, sorted(n for n in (13, 14, 15) if board.lit.get(n))))
        board.sleeps.clear()
        display.test_lights()
        return seen, list(board.sleeps), display.showing, sorted(n for n in (13, 14, 15) if board.lit.get(n))

    seen, sleeps, showing, lit_after = on_board(board, action)
    pins = {"hot": [15], "warm": [14], "cold": [13]}
    for level, got_showing, got_lit in seen:
        assert (got_showing, got_lit) == (level, pins[level]), (
            f"after show({level!r}), showing was {got_showing!r} and the LEDs on were on GP{got_lit}, expected "
            f"{level!r} and only GP{pins[level][0]}: call self.all_off() before you light it"
        )
    assert sleeps == [(1, [13, 14, 15])], (
        f"test_lights() slept {[s for s, _ in sleeps]} with the LEDs on GP{[on for _, on in sleeps]}, expected one "
        f"sleep(1) with all three on"
    )
    assert lit_after == [] and showing == "off", (
        f"after test_lights(), the LEDs on GP{lit_after} were on and showing was {showing!r}, expected the three LEDs "
        f"off and 'off'"
    )


def test_the_log_records_temperatures():
    from log import Log

    log = Log("Alden 101")
    start = (log.place, list(log.temperatures), dict(log.counts))
    assert start == ("Alden 101", [], {"cold": 0, "warm": 0, "hot": 0}), (
        f"Log('Alden 101') started with (place, temperatures, counts) {start}, expected "
        f"('Alden 101', [], {{'cold': 0, 'warm': 0, 'hot': 0}})"
    )
    for fahrenheit, level in ((72.0, "warm"), (81.5, "hot"), (74.0, "warm")):
        log.record(fahrenheit, level)
    got = (log.temperatures, log.counts)
    assert got == ([72.0, 81.5, 74.0], {"cold": 0, "warm": 2, "hot": 1}), (
        f"after recording 72.0 warm, 81.5 hot and 74.0 warm, (temperatures, counts) was {got}, expected "
        f"([72.0, 81.5, 74.0], {{'cold': 0, 'warm': 2, 'hot': 1}})"
    )


def test_the_log_finds_the_highest_lowest_and_average():
    from log import Log

    cases = [
        ([72.0, 81.5, 74.0], 81.5, 72.0, 75.83333),
        ([-5.0, -12.5, -1.0], -1.0, -12.5, -6.16667),
        ([68.0], 68.0, 68.0, 68.0),
        ([60.0, 90.0, 75.0, 90.0], 90.0, 60.0, 78.75),
    ]
    for temperatures, high, low, mean in cases:
        log = Log("test")
        for fahrenheit in temperatures:
            log.record(fahrenheit, "warm")
        got = (log.highest(), log.lowest(), log.average())
        assert close(got[0], high) and close(got[1], low) and abs(float(got[2]) - mean) < 0.001, (
            f"with temperatures {temperatures}, (highest, lowest, average) was {got}, expected ({high}, {low}, "
            f"{mean}): start highest and lowest from the first temperature in the list, not from 0"
        )


def log_value(out, label):
    """Return the value printed after `label` in the thermometer log, normalized."""
    starts = [line.start() for line in re.finditer(r"^\s*THERMOMETER\s+LOG", out, re.IGNORECASE | re.MULTILINE)]
    if not starts:
        return None
    words = r"\s+".join(re.escape(word) for word in label.split())
    match = re.search(rf"^[ \t]*{words}[ \t]*:?[ \t]*([^\n]*)", out[starts[-1]:], re.IGNORECASE | re.MULTILINE)
    if match is None:
        return None
    return " ".join(match.group(1).split()).upper().rstrip(".")


def run_program(capsys, raws, presses, wanted, place):
    import main as program

    board = Board(raws=raws, presses=presses)
    answers = [place, str(wanted)]
    with patch("builtins.input", side_effect=lambda prompt="": answers.pop(0) if answers else ""):
        on_board(board, program.main)
    out, err = capsys.readouterr()
    assert err == "", "the program wrote to the error stream:\n" + err
    return out, board


def check_log(out, board, context, place, temperatures, counts):
    want = {
        "THERMOMETER LOG": place.upper(),
        "Readings": str(len(temperatures)),
        "Cold": str(counts[0]),
        "Warm": str(counts[1]),
        "Hot": str(counts[2]),
    }
    for label, expected in want.items():
        got = log_value(out, label)
        assert got is not None, f'no "{label}" line was printed in the thermometer log ({context})'
        assert got == expected, f'the "{label}" line said {got}, expected {expected} ({context})'
    total = 0
    for temperature in temperatures:
        total += temperature
    for label, expected in (("Highest", round(max(temperatures), 1)), ("Lowest", round(min(temperatures), 1)),
                            ("Average", round(total / len(temperatures), 1))):
        got = log_value(out, label)
        assert got is not None and close(got, expected), (
            f'the "{label}" line said {got}, expected {expected} ({context})'
        )
    assert not any(board.lit.get(number) for number in (13, 14, 15)), (
        f"a light was still on when the program ended ({context}): all_off turns the three LEDs off"
    )


def test_the_program_reads_the_temperature_and_logs_it(capsys):
    # Roughly 66, 72, 75 and 84 degrees Fahrenheit
    raws = [14400, 14184, 14075, 13750]
    temperatures = [fahrenheit_of(raw) for raw in raws]
    out, board = run_program(capsys, raws, [], 4, "Alden 101")
    check_log(out, board, "4 readings, no press", "Alden 101", temperatures, (1, 2, 1))


def test_the_program_stops_when_the_button_is_pressed(capsys):
    raws = [13750, 13750, 13750, 13750, 13750]
    temperatures = [fahrenheit_of(raw) for raw in raws[:2]]
    # test_lights sleeps for 1 second, then each reading sleeps for 1 more before the button is read
    out, board = run_program(capsys, raws, [(2.5, 3.5)], 5, "Carr Hall")
    check_log(out, board, "5 readings asked for, button pressed during the second", "Carr Hall", temperatures, (0, 0, 2))
