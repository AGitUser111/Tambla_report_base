import time
from functools import partial


# value to differentiate regular functions
NO_EXPECTATION = object()


class Retry:
    """ This is a retry class that you can use to retry a loop of functions with expectations.

    Here is an example:

        loop = Retry(debug=True)                                                    # this gives an instance of the Retry class with debug mode enabled
        loop.add_func(switch_report_tab, page, tab=ReportTab.TimeAttendance)        # add a function to the loop (function is not called yet) and pass in the arguments for the function
        loop.add_func(
            select_report_type,
            page,
            report_type=ReportType.ScheduleAndTimeSheetComparison,
        )
        loop.add_func(select_report_format, page, file_format=ReportFormat.CSV)
        loop.add_func(select_org_unit, page, org_units=[OrgUnit.HolyCrossLaundry])
        loop.add_func(click_background, page)
        loop.add_func(run_report, page)
        loop.add_func(
            ResponseCheck.check_response,
            expected_response="Your request is being processed",
            expect_val=True,
        )                                                                          # add a conditional function to the loop. This function will only pass if the function returns the expect_val.
        if not loop.run(retries=3, delay=0):                                       # run the loop with 3 retries and no delay between retries. If the loop fails, it will print a message.
            print("Failed to run report.")
            return

    """
    def __init__(self, debug=False):
        self.loop: list[tuple[partial, object]] = [] # list of functions and expectations
        self.debug = debug # debug mode flag to print debug messages

    def _log(self, message: str):
        """
        Log debug messages if debug mode is enabled.
        
        Args:
            message (str): The message to log.
        
        Returns:
            None
        """
        if self.debug:
            print(message)

    def add_func(self, function: callable, *args, expect_val=NO_EXPECTATION, **kwargs):
        """
        Add a function and an expected return value. If the function doesn't return the expected value, the loop will be retried. 
        If no expect_val is provided, the function will have no effect on the retry loop.
        
        Args:
            function (callable): The function to add to the loop.
            *args: The arguments to pass to the function.
            expect_val (object): The expected return value of the function. Defaults to NO_EXPECTATION.
            **kwargs: The keyword arguments to pass to the function.
            
        Returns:
            None
        """
        partial_function = partial(function, *args, **kwargs)
        self.loop.append((partial_function, expect_val))  # Use provided expected value

    def run(self, retries=3, delay=0):
        """
        Runs the retry loop.

        Executes all functions in the order they were added. Conditional functions
        are evaluated to decide if the loop should exit early or retry.

        Args:
            retries (int): The number of times to retry the loop if it fails. Defaults to 3.
            delay (int): The time to wait (in seconds) between retries. Defaults to 0.

        Returns:
            bool: True if all functions succeed and conditions are met. False if the retry
                  limit is reached.
        """
        for attempt in range(1, retries + 1):
            self._log(f"--- Attempt {attempt} of {retries} ---")
            success = True  # Track if all functions and conditions succeed

            for func, expected in self.loop:
                try:
                    self._log(f"Running function: {func.func.__name__}")
                    # Check if function has an expectation
                    result = func()
                    if expected is not NO_EXPECTATION:  # Conditional function
                        self._log(
                            f"Checking response: {func.func.__name__} -> Got {result}, Expected {expected}")
                        if result != expected:
                            success = False  # Condition failed
                            break  # Exit the loop early
                except Exception as e:
                    self._log(f"Error in {func.func.__name__}: {e}")
                    success = False
                    break  # Exit early on any exception

            if success:
                self._log(
                    "All functions succeeded and conditions met. Exiting retry loop."
                )
                return True

            # Wait before the next retry
            if delay > 0:
                time.sleep(delay)

        self._log("Retry limit reached. Exiting retry loop.")
        return False
