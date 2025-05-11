"""PWM Fan speed control"""
from math import log10
from machine import Pin, PWM


class FanControl:
    """Class to handle controlling a fan speed

    Utilizes four points to create a fan curve
        1. Boolean if zero RPM mode is supported
        2. Temperature at or below to set minimum speed (30% PWM)
        3. Temperature at or above to set maximum speed (100% PWM)
        4. Type of interpolation (linear, logarithmic, exponential)
    """

    def __init__(self, pin: int):
        """Used to control the speed of a PWM fan based on a temperature reading. Use `define_curve`
        to change the configurable values. There are currently a few assumptions that aren't
        configurable.
            1. PWM will be set with a 16 bit value
            2. PWM frequency should match the intel whitepaper at 25kHz
            3. Minimum startup fan speed matches the intel whitepaper at 30% PWM Duty
            4. Signal is not inverted, 100% duty cycle is 100% fan speed

        There are a few variables that can be configured using the define_curve method
            1. zero_rpm mode: a Zero RPM fan can turn off when the PWM duty signal is zero. If this
            is set on a fan that isn't compatible the fan speed will decrease below 30% but will not
            stop turning
            2. min_temp: Any reading at or below this temperature will set the fan to either 0 RPM
            or 30% RPM based on zero_rpm mode
            3. max_temp: Any reading at or below this temperature will set the fan to 100% RPM
            4. interpolation: Choose what type of curve is used between the minimum and maximum
            setting. this can be linear, logarithmic, or exponential depending on how quickly the
            fan should ramp up with temperature changes

        Example:
            ```
            # Example using thermistor.py to get a temperature reading
            import time
            from fan_pwm import FanControl
            from thermistor import Thermistor

            pwm_controller = FanControl(15)

            _ = Pin(28, Pin.IN)
            adc = ADC(2)
            thermistor = Thermistor(adc)

            while True:
                temp = thermistor.ntc()
                pwm_controller.set_fan(temp)
                time.sleep(1)
            ```
        Args:
            pin (int): integer representing the pin that will be the PWM output
        """
        pwm_frequency = 25000
        self.maximum = 65535  # 2^16-1 The highest value you can send with PWM.duty_u16
        self.minimum = int(self.maximum * 0.3)  # Minimum startup PWM is defined as 30%
        self.pwm = PWM(Pin(pin), freq=pwm_frequency)
        # Values to be used by the fan curve
        self.zero_rpm = False
        self.min_temp = 25
        self.max_temp = 50
        self.interpolation = "linear"

    def _calculate_speed(self, temp: float) -> int:
        """Determine which fan curve to use and return the integer to set the PWM duty at

        Args:
            temp (float): temperature reading

        Returns:
            int: integer representing the PWM duty cycle to set
        """
        if "linear" in self.interpolation:
            return self._calculate_speed_linear(temp)
        if "logarithmic" in self.interpolation:
            return self._calculate_speed_logarithmic(temp)
        return self._calculate_speed_exponential(temp)

    def _calculate_speed_exponential(self, temp: float) -> int:
        """Exponential fan curve meaning temps increase slowly early in the curve and then quickly
        as it approaches the maximum speed

        Equation calculating a scale with linear x axis (Temp) and logarithmic y axis (RPM)
        Uses log base 10

        y = y0*10^(((x-x0)/(x1-x0))*log((y1/y0)))
        from the default values
            y = 0.3*10^(((x-25)/25)*log(1/0.3))
            y = 0.3*10^(0.021*(x-25))

        Args:
            temp (float): temperature reading

        Returns:
            int: integer representing the PWM duty cycle to set
        """
        log_ys = log10((1 / 0.3))  # log((y1/y0))
        x_ratio = (temp - self.min_temp) / (self.max_temp - self.min_temp)  # ((x-x0)/(x1-x0))
        exponent = x_ratio * log_ys  # ((x-x0)/(x1-x0))*log((y1/y0))
        exponentiation = 10**exponent  # 10^(((x-x0)/(x1-x0))*log((y1/y0)))
        interpolate = 0.3 * exponentiation  # y0*10^(((x-x0)/(x1-x0))*log((y1/y0)))
        return int(self.maximum * interpolate)

    def _calculate_speed_logarithmic(self, temp: float) -> int:
        """Logarithmic fan curve meaning temps increase quickly early in the curve and slow as it
        approaches the maximum speed

        Equation calculating a scale with logarithmic x axis (Temp) and linear y axis (RPM)
        Uses log base 10

        y = (y1-y0)*(log((x/x0))/log((x1/x0))) + y0
        from the default values
            y = (1-0.3)*(log((x/25))/log((50/25))) + 0.3
            y = 0.7*(log(x/25)/1.398) + 0.3

        Args:
            temp (float): temperature reading

        Returns:
            int: integer representing the PWM duty cycle to set
        """
        multiplicand = 1 - 0.3  # y1 - y0
        top_log = log10((temp / self.min_temp))  # log((x/x0))
        bottom_log = log10((self.max_temp / self.min_temp))  # log((x1/x0))
        quotient = top_log / bottom_log  # log((x/x0))/log((x1/x0))
        product = multiplicand * quotient  # (y1-y0)*(log((x/x0))/log((x1/x0)))
        interpolate = product + 0.3  # y = (y1-y0)*(log((x/x0))/log((x1/x0))) + y0
        return int(self.maximum * interpolate)

    def _calculate_speed_linear(self, temp: float) -> int:
        """Use linear interpolation to set the fan speed at any temperature

        y = y0 + (x-x0)((y1-y0)/(x1-x0))
        from the default values
            y = 0.3 + (x-25)((1-0.3)/(50-25))
            y = 0.3 + (x-25)0.028

        Args:
            temp (float): temperature reading

        Returns:
            int: integer representing the PWM duty cycle to set
        """
        diff_pwm = 1 - 0.3  # This is y1 - y0 min_rpm is 30% and max_rpm is 100%
        diff_temp = self.max_temp - self.min_temp  # This is x1 - x0
        slope = diff_pwm / diff_temp
        interpolate = 0.3 + ((temp - self.min_temp) * slope)
        return int(self.maximum * interpolate)

    def define_curve(
        self, zero_rpm: bool, min_temp: int, max_temp: int, interpolation: str
    ) -> None:
        """Customize the fan curve parameters

        Args:
            zero_rpm (bool): if zero RPM mode is supported and desired
            min_temp (int): Temperature at which fan turns on at 30%
            if zero_rpm is false all temps under this will be 30% speed as well
            max_temp (int): Temperature at which fan speed goes to 100%
            interpolation (str): Method to calculate fan percentage between min and max
        """
        self.zero_rpm = zero_rpm
        self.min_temp = min_temp
        self.max_temp = max_temp
        self.interpolation = (
            interpolation
            if [interpolation in option for option in ("linear, exponential, logarithmic")]
            else self.interpolation
        )

    def set_fan(self, temp: float) -> None:
        """Method to change the fan speed via PWM based on current temperature and the configured
        fan curve

        Args:
            temp (int): monitored temperature to set fan speed via
        """
        if temp < self.min_temp and self.zero_rpm:
            self.pwm.duty_u16(0)
        elif temp <= self.min_temp:
            self.pwm.duty_u16(self.minimum)
        elif temp >= self.max_temp:
            self.pwm.duty_u16(self.maximum)
        else:
            speed = self._calculate_speed(temp)
            self.pwm.duty_u16(speed)
