import os
import time
from dataclasses import dataclass
from datetime import date
from enum import Enum

from dotenv import load_dotenv
from playwright.sync_api import (
    Browser,
    BrowserContext,
    ElementHandle,
    Locator,
    Page,
    Response,
    sync_playwright,
)

from constants import (
    JoelsOrgTemplates,
    OrgTemplate,
    OrgUnit,
    ReportFormat,
    ReportStatus,
    ReportTab,
    ReportType,
)
from retry import Retry
from utils import ResponseCheck

""" 
This makes use of the python-dotenv package to load environment variables from a .env file.
Feel free to change how you handle username and passwords.

If using python-dotenv:
1) install the package using pip: pip install python-dotenv
2) create a .env file (.env is the whole name of the file) that contains the following:
    TAMBLA_USER=put_your_username_here
    TAMBLA_PASSWORD=put_your_password_here
"""


@dataclass
class ReportDetails:
    """Dataclass to store report details. These are retrieved from the server response."""

    def __init__(self, **kwargs):
        self.id: str = kwargs.get("Id")

        self.server_filepath: str = kwargs.get("ReportFileName")

        self.filename_ext: str = self.server_filepath.split("\\")[
            -1
        ].lower()  # Get filename from server path with extension (e.g. "report.csv")

        self.filetype: str = self.filename_ext.split(".")[
            -1
        ]  # Get filetype from filename (e.g. "csv")

        self.filename: str = self.filename_ext.removesuffix(
            f".{self.filetype}"
        )  # Get filename without extension (e.g. "report")

        self.report_type = kwargs.get(
            "ReportName"
        )  # Report type (e.g. "Schedule and Timesheet Comparison")

        self.status: str = kwargs.get(
            "ReportStatus"
        )  # Report status (e.g. "Processing")

        self.download_url: str = (
            f"https://etivity.comops.biz/ERP/RequestPreview/PrintPreview?reportRequestId={self.id}&reportName=\\{self.server_filepath}&reportStatus={self.status}"
        )
        self.report_date: str = kwargs.get(
            "ReportDate"
        )  # Date report was generated - according to server

        self.report_date_str: str = kwargs.get(
            "ReportDateStr"
        )  # Date report was generated as string - according to server

        self.error_message: str = kwargs.get("ErrorMessage")


def main():
    load_dotenv(override=True)
    with sync_playwright() as p:
        browser: Browser = p.chromium.launch(headless=False, slow_mo=1000)
        context: BrowserContext = browser.new_context()
        page: Page = context.new_page()

        def handle_response(response: Response):
            if "RequestReport" in response.url:  # Match response for report requests
                try:
                    print(response.url)
                    ResponseCheck.set_response(response.json().get("Message"))
                except Exception as e:
                    print(f"Failed to log response: {e}")

        # Attach response listener
        page.on("response", handle_response)

        login(
            page,
            username=os.getenv("TAMBLA_USER"),
            password=os.getenv("TAMBLA_PASSWORD"),
        )
        goto_reports_page(page)

        switch_report_tab(page, tab=ReportTab.TimeAttendance)
        select_report_type(
            page,
            report_type=ReportType.TotalHoursWorked,
        )
        select_report_format(page, file_format=ReportFormat.EXCEL)
        select_date_range(
            page, start_date=date(2024,12, 2), end_date=date(2024, 12, 8)
        )
        # select_org_unit(page, org_units=[OrgUnit.HolyCrossLaundry])
        select_org_template(page, org_template=JoelsOrgTemplates.HolyCrossLaundry)
        click_background(page)
        run_report(page)
        page.pause()
        if not ResponseCheck.check_response(
            expected_response="Your request is being processed",
        ):
            print("Failed to run report.")
            return
        switch_report_tab(page, tab=ReportTab.Reports)

        most_recent_report: ReportDetails = get_report_details(page)
        download_report(page, most_recent_report)

        browser.close()


def get_report_data(page: Page, report_details: ReportDetails) -> str:
    """
    Get the report data from the server.

    Args:
        page (Page): The playwright page object.
        report_details (ReportDetails): The report details object.

    Returns:
        str: The report data.
    """
    response = page.request.get(report_details.download_url)
    if response.status == 200:
        return response.body()
    else:
        return None


def download_report(page: Page, report_details: ReportDetails, filepath=None) -> None:
    """
    Get the report data and save it to a file.

    Args:
        page (Page): The playwright page object.
        report_details (ReportDetails): The report details object.
        filepath (str): The filepath to save the report to. Defaults to current directory.

    Returns:
        None
    """
    if response := get_report_data(page, report_details):
        filepath = filepath if filepath else report_details.filename_ext
        with open(filepath, "wb") as file:
            file.write(response)
        print(f"{report_details.filename_ext} downloaded successfully")
    else:
        print(f"{report_details.filename_ext} failed to download")


def login(page: Page, username: str, password: str) -> None:
    page.goto("https://etivity.comops.biz/Account/Login?ReturnUrl=%2fEtivity")
    page.get_by_placeholder("USERNAME").fill(username)
    page.get_by_placeholder("PASSWORD").fill(password)
    page.get_by_role("button", name="Login").click()


def goto_reports_page(page: Page) -> None:
    page.locator("a").filter(has_text="Reports").click()
    page.wait_for_load_state("networkidle")


def switch_report_tab(page: Page, tab: ReportTab = ReportTab.TimeAttendance) -> None:
    if not isinstance(tab, ReportTab):
        raise ValueError("Invalid report type provided.")
    page.locator(tab.value).click()
    page.wait_for_load_state("networkidle")
    time.sleep(5)


def select_report_type(page: Page, report_type: ReportType) -> None:
    if not isinstance(report_type, ReportType):
        raise ValueError("Invalid report type provided.")
    page.locator("#ddlReportName").select_option(report_type.value)
    page.wait_for_load_state("networkidle")
    time.sleep(1)


def select_report_format(page: Page, file_format: ReportFormat) -> None:
    if not isinstance(file_format, ReportFormat):
        raise ValueError("Invalid file format provided.")
    page.locator("#ddlReportFormat").select_option(file_format.value)
    page.wait_for_load_state("networkidle")
    time.sleep(1)


def select_org_unit(page: Page, org_units: list[OrgUnit]) -> None:
    if not all(isinstance(unit, OrgUnit) for unit in org_units):
        raise ValueError("Invalid organisation unit provided.")

    for unit in org_units:
        page.locator("#divOrganisationTreeContainer").get_by_role(
            "treeitem", name=unit.value
        ).get_by_role("checkbox").click()
        page.wait_for_load_state("load")
        page.wait_for_load_state("networkidle")
        time.sleep(1)
        page.get_by_role("button", name="OK").click()
        page.wait_for_load_state("load")
        page.wait_for_load_state("networkidle")


def select_org_template(page: Page, org_template: OrgTemplate) -> None:
    if not isinstance(org_template, OrgTemplate):
        raise ValueError(
            "Invalid organisation template provided. Please check the constants file and add your own."
        )
    page.locator("#ddlOrgProfile").select_option(org_template.value)
    page.wait_for_load_state("load")
    page.wait_for_load_state("networkidle")
    time.sleep(1)


def click_background(page: Page) -> None:
    page.locator("#module-container section").first.click()
    page.wait_for_load_state("networkidle")


def run_report(page: Page) -> None:
    page.get_by_role("link", name="Manage").click()
    page.get_by_role("link", name="Report Request").click()
    page.get_by_role("button", name="OK").click()


def reload_report_page(page: Page) -> None:
    page.locator("#reloadPage").click()
    page.wait_for_load_state("networkidle")


def get_report_details(page: Page, report_index: int = 0) -> ReportDetails:
    while True:
        with page.expect_response(
            "https://etivity.comops.biz/ERP/RequestPreview/RequestPreview"
        ) as response_info:
            reload_report_page(page)
        if not response_info:
            continue
        response_value: dict = response_info.value.json()
        response_data: list = response_value.get("Data")
        report: ReportDetails = ReportDetails(**response_data[report_index])

        print(f"Most recent report URL: {report.download_url}")

        if report.status == ReportStatus.Processing.value:
            time.sleep(2)
        else:
            return report


def select_date_range(page: Page, start_date: date, end_date: date) -> None:
    """Select a date range on the report page.

    Args:
        page (Page): The playwright page object.
        start_date (date): The start date.
        end_date (date): The end date.

    Returns:
        None
    """
    if not all(isinstance(date_obj, date) for date_obj in [start_date, end_date]):
        raise ValueError("Invalid date object provided.")

    # Select date range option
    page.locator("#radDateRange").check()

    # Click on the date input
    page.locator("#txtAvailabilityProfilesDateRange").click()

    # Gather all of the start date elements
    start_year_element: Locator = page.locator(
        "div:nth-child(10) > div > .calendar-date > .table-condensed > thead > tr > th:nth-child(2) > .yearselect"
    ).nth(1)
    start_year_element.select_option(str(start_date.year))
    
    start_month_element: Locator = page.locator(
        "div:nth-child(10) > div > .calendar-date > .table-condensed > thead > tr > th:nth-child(2) > .monthselect"
    ).nth(1)
    start_month_element.select_option(str(start_date.month - 1))

    start_day_elements: list[ElementHandle] = page.locator(
        "div:nth-child(10) > .left > .calendar-date > .table-condensed > tbody > tr > td"
    ).element_handles()

    start_day_element: ElementHandle = [
        element
        for element in start_day_elements
        if "off" not in element.get_attribute("class")
        and element.inner_text() == str(start_date.day)
    ][0]
    start_day_element.click()


    # Gather all of the end date elements
    end_year_element: Locator = page.locator(
        "div:nth-child(10) > div > .calendar-date > .table-condensed > thead > tr > th:nth-child(2) > .yearselect"
    ).nth(1)
    end_year_element.select_option(str(end_date.year))
    
    end_month_element: Locator = page.locator(
        "div:nth-child(10) > div > .calendar-date > .table-condensed > thead > tr > th:nth-child(2) > .monthselect"
    ).nth(1)
    end_month_element.select_option(str(end_date.month - 1))

    end_day_elements: list[ElementHandle] = page.locator(
        "div:nth-child(10) > .right > .calendar-date > .table-condensed > tbody > tr > td"
    ).element_handles()

    end_day_element: ElementHandle = [
        element
        for element in end_day_elements
        if "off" not in element.get_attribute("class")
        and element.inner_text() == str(end_date.day)
    ][0]

    end_day_element.click()

    # Apply the date range
    page.get_by_role("button", name="Apply").click()


if __name__ == "__main__":
    main()
