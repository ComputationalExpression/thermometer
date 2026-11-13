"""Automated checks for Lab 8: Thermometer.

Each class is checked on its own, on a pretend board, so a check passes or fails
on one file alone, whatever state the other files are in. The pretend DHT22
reports the temperature and humidity each check chooses, and only after
measure() is called. The pretend chip sensor reports the raw numbers each check
chooses. The program checks run main with all four classes together and read
only the thermometer log at the end, not the narrative lines. Log values forgive
extra spaces, letter case, and a missing colon.

Time passes only when the code calls sleep. When a check fails, the assertion
message says what came out wrong and what was expected. gatorgrade does not show
that message itself; it prints the pytest command to run.
"""

import importlib
import re
from unittest.mock import patch

import dht
import mockro
from machine import ADC, Pin

MODULES = ("sensors", "comfort", "display", "log", "main")
# A raw reading of 14184 from the chip is about 72 degrees Fahrenheit
ROOM = 14184


def chip_fahrenheit(raw):
    """The temperature the formulas in the README give for one raw chip reading."""
    voltage = raw * 3.3 / 65535
    return (27 - (voltage - 0.706) / 0.001721) * 9 / 5 + 32


def fahrenheit_of(celsius):
    return celsius * 9 / 5 + 32


def close(got, expected, within=0.01):
    try:
        return abs(float(got) - expected) < within
    except (TypeError, ValueError):
        return False


class Board:
    """The pins and sensors of a pretend Pico, with pins told apart by GP number.

    `air` is the list of (celsius, humidity) the DHT22 measures in turn, and `raws`
    the list of numbers the chip sensor reports in turn. `presses` is a list of
    (start, end) times in seconds: the button reads 0 while the clock is inside
    one of them. `clock` adds up the time slept, and `sleeps` keeps which LEDs were
    lit during each sleep.
    """

    def __init__(self, air=None, raws=None, presses=None):
        self.air = list(air or [])
        self.raws = list(raws or [])
        self.presses = list(presses or [])
        self.clock = 0.0
        self.numbers = {}
        self.inputs = set()
        self.lit = {}
        self.sleeps = []
        self.measured = None
        self.measures = 0
        self.dht_pins = []

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
        return self.raws.pop(0) if self.raws else ROOM

    def dht_init(self, pin):
        self.dht_pins.append(pin)

    def measure(self):
        self.measures += 1
        self.measured = self.air.pop(0) if self.air else (22.0, 45.0)

    def temperature(self):
        return None if self.measured is None else self.measured[0]

    def humidity(self):
        return None if self.measured is None else self.measured[1]


def adc_channels():
    return [args[2] for args, _ in mockro.get_recorder().calls("machine.ADC.__init__") if len(args) >= 3]


def on_board(board, action):
    """Run `action()` with the pins and sensors wired to `board` and sleep patched."""
    mockro.get_recorder().clear()
    stubs = [
        patch("time.sleep", side_effect=board.sleep),
        patch.object(ADC, "read_u16", board.read_u16),
        patch.object(dht.DHT22, "__init__", board.dht_init),
        patch.object(dht.DHT22, "measure", board.measure),
        patch.object(dht.DHT22, "temperature", board.temperature),
        patch.object(dht.DHT22, "humidity", board.humidity),
    ]
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


def test_the_sensors_start_and_measure_the_air():
    from sensors import Sensors

    board = Board(air=[(21.5, 44.0), (23.0, 52.5)])

    def action():
        sensors = Sensors(2)
        start = (sensors.air_celsius, sensors.humidity, sensors.readings, adc_channels(),
                 [board.number(pin) for pin in board.dht_pins])
        sensors.read_air()
        first = (sensors.air_celsius, sensors.humidity, sensors.readings)
        sensors.read_air()
        second = (sensors.air_celsius, sensors.humidity, sensors.readings)
        return start, first, second

    (celsius, humidity, readings, channels, dht_pins), first, second = on_board(board, action)
    assert channels == [4], f"Sensors(2) made ADC objects on {channels}, expected one on channel 4: ADC(4)"
    assert dht_pins == [2], f"Sensors(2) made DHT22 sensors on GP{dht_pins}, expected one: dht.DHT22(Pin(air_pin))"
    assert (celsius, humidity, readings) == (0, 0, 0), (
        f"after Sensors(2), (air_celsius, humidity, readings) was {(celsius, humidity, readings)}, expected (0, 0, 0)"
    )
    for got, want, when in ((first, (21.5, 44.0, 1), "the first"), (second, (23.0, 52.5, 2), "the second")):
        assert got == want, (
            f"after {when} read_air(), (air_celsius, humidity, readings) was {got}, expected {want}: call measure() "
            f"on the DHT22 first, then keep its temperature() and humidity(), and add 1 to readings"
        )


def test_the_sensors_convert_and_compare():
    from sensors import Sensors

    board = Board(air=[(20.0, 40.0)], raws=[14184, 13750, 14400])

    def action():
        sensors = Sensors(2)
        sensors.read_air()
        return sensors.air_fahrenheit(), sensors.chip_fahrenheit(), sensors.difference(), sensors.difference()

    air, chip, difference, again = on_board(board, action)
    assert close(air, 68.0), (
        f"air_fahrenheit() returned {air} after the DHT22 measured 20.0 degrees Celsius, expected 68.0: "
        f"air_celsius times 9, divided by 5, plus 32"
    )
    assert close(chip, chip_fahrenheit(14184)), (
        f"chip_fahrenheit() returned {chip} for a raw reading of 14184, expected {chip_fahrenheit(14184):.2f}: "
        f"read_u16() on ADC(4), then the voltage, Celsius and Fahrenheit formulas in the README"
    )
    for got, raw in ((difference, 13750), (again, 14400)):
        want = chip_fahrenheit(raw) - 68.0
        assert close(got, want), (
            f"difference() returned {got} with the chip reading {raw} and the air at 68.0 F, expected {want:.2f}: "
            f"self.chip_fahrenheit() minus self.air_fahrenheit()"
        )


def test_comfort_sorts_a_temperature_and_a_humidity():
    from comfort import Comfort

    comfort = Comfort(68, 78, 30, 60)
    got = (comfort.cold_below, comfort.hot_above, comfort.dry_below, comfort.humid_above)
    assert got == (68, 78, 30, 60), (
        f"Comfort(68, 78, 30, 60) stored (cold_below, hot_above, dry_below, humid_above) {got}, expected (68, 78, 30, 60)"
    )
    for fahrenheit, want in ((50, "cold"), (67.9, "cold"), (68, "warm"), (72, "warm"), (78, "warm"), (78.1, "hot")):
        got = comfort.level(fahrenheit)
        assert got == want, (
            f"level({fahrenheit}) with Comfort(68, 78, 30, 60) returned {got!r}, expected {want!r}: below "
            f"cold_below is cold, above hot_above is hot, and anything else, including the dividing values, is warm"
        )
    for humidity, want in ((20, "dry"), (29.9, "dry"), (30, "comfortable"), (45, "comfortable"), (60, "comfortable"),
                           (60.1, "humid")):
        got = comfort.humidity_level(humidity)
        assert got == want, (
            f"humidity_level({humidity}) with Comfort(68, 78, 30, 60) returned {got!r}, expected {want!r}: below "
            f"dry_below is dry, above humid_above is humid, and anything else is comfortable"
        )
    other = Comfort(30, 40, 10, 20)
    assert other.level(35) == "warm" and other.humidity_level(25) == "humid", (
        "Comfort(30, 40, 10, 20) did not use those numbers: compare with the attributes stored in __init__"
    )


def test_comfort_describes_a_reading():
    from comfort import Comfort

    comfort = Comfort(68, 78, 30, 60)
    for fahrenheit, humidity, want in ((72, 45, True), (72, 65, False), (60, 45, False), (85, 20, False)):
        got = comfort.is_comfortable(fahrenheit, humidity)
        assert got is want, (
            f"is_comfortable({fahrenheit}, {humidity}) with Comfort(68, 78, 30, 60) returned {got!r}, expected {want}: "
            f"True only when the level is warm and the humidity level is comfortable"
        )
    for fahrenheit, humidity, words in ((72.46, 44.04, ("72.5", "warm", "44.0", "comfortable")),
                                        (85.04, 71.25, ("85.0", "hot", "71.2", "humid"))):
        got = comfort.describe(fahrenheit, humidity)
        assert isinstance(got, str), f"describe({fahrenheit}, {humidity}) returned {got!r}, expected a string"
        missing = [word for word in words if word not in got.lower()]
        assert not missing, (
            f"describe({fahrenheit}, {humidity}) returned {got!r}, which is missing {missing}: it needs the "
            f"temperature and the humidity, each rounded to one decimal place, and both levels"
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


def test_the_display_shows_flashes_and_tests_its_lights():
    from display import Display

    board = Board()

    def action():
        display = Display(15, 14, 13)
        seen = []
        for level in ("hot", "cold", "warm"):
            display.show(level)
            seen.append((level, display.showing, sorted(n for n in (13, 14, 15) if board.lit.get(n))))
        board.sleeps.clear()
        display.flash("cold")
        flashed = (list(board.sleeps), display.showing, sorted(n for n in (13, 14, 15) if board.lit.get(n)))
        board.sleeps.clear()
        display.test_lights()
        tested = (list(board.sleeps), display.showing, sorted(n for n in (13, 14, 15) if board.lit.get(n)))
        return seen, flashed, tested

    seen, flashed, tested = on_board(board, action)
    pins = {"hot": [15], "warm": [14], "cold": [13]}
    for level, got_showing, got_lit in seen:
        assert (got_showing, got_lit) == (level, pins[level]), (
            f"after show({level!r}), showing was {got_showing!r} and the LEDs on were on GP{got_lit}, expected "
            f"{level!r} and only GP{pins[level][0]}: call self.all_off() before you light it"
        )
    assert flashed == ([(0.5, [13])], "off", []), (
        f"flash('cold') slept {[s for s, _ in flashed[0]]} with the LEDs on GP{[on for _, on in flashed[0]]}, and "
        f"left showing {flashed[1]!r} with GP{flashed[2]} on, expected one sleep(0.5) with only GP13 on, then "
        f"the three LEDs off and showing 'off': self.show(level), sleep(0.5), then self.all_off()"
    )
    assert tested == ([(1, [13, 14, 15])], "off", []), (
        f"test_lights() slept {[s for s, _ in tested[0]]} with the LEDs on GP{[on for _, on in tested[0]]}, "
        f"expected one sleep(1) with the three LEDs on, then the three off and showing 'off'"
    )


def test_the_log_records_readings():
    from log import Log

    log = Log("Alden 101")
    start = (log.place, list(log.temperatures), list(log.humidities), dict(log.counts))
    assert start == ("Alden 101", [], [], {"cold": 0, "warm": 0, "hot": 0}), (
        f"Log('Alden 101') started with (place, temperatures, humidities, counts) {start}, expected "
        f"('Alden 101', [], [], {{'cold': 0, 'warm': 0, 'hot': 0}})"
    )
    for fahrenheit, humidity, level in ((72.0, 45.0, "warm"), (81.5, 62.0, "hot"), (74.0, 50.5, "warm")):
        log.record(fahrenheit, humidity, level)
    got = (log.temperatures, log.humidities, log.counts)
    want = ([72.0, 81.5, 74.0], [45.0, 62.0, 50.5], {"cold": 0, "warm": 2, "hot": 1})
    assert got == want, (
        f"after recording (72.0, 45.0, warm), (81.5, 62.0, hot) and (74.0, 50.5, warm), "
        f"(temperatures, humidities, counts) was {got}, expected {want}"
    )


def test_the_log_finds_the_highest_lowest_and_average_humidity():
    from log import Log

    cases = [
        ([72.0, 81.5, 74.0], [45.0, 62.0, 50.5], 81.5, 72.0, 52.5),
        ([-5.0, -12.5, -1.0], [20.0, 25.0, 30.0], -1.0, -12.5, 25.0),
        ([68.0], [41.0], 68.0, 68.0, 41.0),
    ]
    for temperatures, humidities, high, low, mean in cases:
        log = Log("test")
        for fahrenheit, humidity in zip(temperatures, humidities):
            log.record(fahrenheit, humidity, "warm")
        got = (log.highest(), log.lowest(), log.average_humidity())
        assert close(got[0], high) and close(got[1], low) and close(got[2], mean, 0.001), (
            f"with temperatures {temperatures} and humidities {humidities}, (highest, lowest, average_humidity) "
            f"was {got}, expected ({high}, {low}, {mean}): start highest and lowest from the first temperature in "
            f"the list, not from 0"
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


def run_program(capsys, air, raws, presses, wanted, place):
    import main as program

    board = Board(air=air, raws=raws, presses=presses)
    answers = [place, str(wanted)]
    with patch("builtins.input", side_effect=lambda prompt="": answers.pop(0) if answers else ""):
        on_board(board, program.main)
    out, err = capsys.readouterr()
    assert err == "", "the program wrote to the error stream:\n" + err
    return out, board


def check_log(out, board, context, place, air, counts, chip_raw):
    temperatures = [fahrenheit_of(celsius) for celsius, _ in air]
    humidities = [humidity for _, humidity in air]
    want = {"THERMOMETER LOG": place.upper(), "Readings": str(len(air)), "Cold": str(counts[0]),
            "Warm": str(counts[1]), "Hot": str(counts[2])}
    for label, expected in want.items():
        got = log_value(out, label)
        assert got is not None, f'no "{label}" line was printed in the thermometer log ({context})'
        assert got == expected, f'the "{label}" line said {got}, expected {expected} ({context})'
    numbers = {
        "Highest": round(max(temperatures), 1),
        "Lowest": round(min(temperatures), 1),
        "Average humidity": round(sum(humidities) / len(humidities), 1),
        "Chip minus air": round(chip_fahrenheit(chip_raw) - temperatures[-1], 1),
    }
    for label, expected in numbers.items():
        got = log_value(out, label)
        assert got is not None and close(got, expected, 0.06), (
            f'the "{label}" line said {got}, expected {expected} ({context})'
        )
    assert board.measures == len(air), (
        f"the DHT22 measured {board.measures} times for {len(air)} readings ({context}): read_air() measures once"
    )
    assert not any(board.lit.get(number) for number in (13, 14, 15)), (
        f"a light was still on when the program ended ({context}): all_off turns the three LEDs off"
    )


def test_the_program_reads_both_sensors_and_logs_them(capsys):
    # 68.0 F comfortable, 72.5 F comfortable, 78.8 F humid, 64.4 F dry
    air = [(20.0, 45.0), (22.5, 55.0), (26.0, 70.0), (18.0, 25.0)]
    out, board = run_program(capsys, air, [13750], [], 4, "Alden 101")
    check_log(out, board, "4 readings, no press", "Alden 101", air, (1, 2, 1), 13750)
    flashes = [lit for seconds, lit in board.sleeps if seconds == 0.5]
    assert [15] in flashes and [13] in flashes, (
        "the hot LED did not flash for the humid reading, or the cold LED for the dry one: flash(level) lights "
        "the LED for half a second, then turns it off"
    )


def test_the_program_stops_when_the_button_is_pressed(capsys):
    air = [(26.0, 45.0)] * 5
    # test_lights sleeps for 1 second, then each reading waits 2 more before the button is read
    out, board = run_program(capsys, air, [14184], [(4.0, 5.5)], 5, "Carr Hall")
    check_log(out, board, "5 readings asked for, button pressed during the second", "Carr Hall", air[:2], (0, 0, 2),
              14184)
