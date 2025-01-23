from enum import Enum

class ReportType(Enum):
    """Report types available in the system. These are used to select the report type in the dropdown menu."""
    #### Time and Attendance Reports ####
    BankAccruals = "94"
    ClockDevice = "14"
    ContractedHoursComparison = "100"
    Cost = "13"
    Evacuation = "59"
    EventVariance = "80"
    Exception = "12"
    LeaveTaken = "45"
    ManualEventTimesheet = "54"
    ManualTimesheet = "35"
    PayAdjustmentSummary = "96"
    PayComparisonSummary = "95"
    PayrollDetails = "28"
    PayrollHoursBreakdown = "98"
    RawClockingComparison = "87"
    RejectedClocking = "67"
    ResourceClockingDetails = "10"
    ResourceNotWorked = "86"
    ResourcePaidHours = "66"
    ResourcePayGroupException = "33"
    ResourcePeriodToDateHours = "85"
    ResourceSignOff = "61"
    ScheduleAndTimeSheetComparison = "57"
    SignOffSheet = "76"
    TAActivityCode = "92"
    TADepartmentActivity = "88"
    TADetails = "69"
    TAPeriodToDateSummary = "72"
    TASignOff = "39"
    TAVariance = "30"
    TAVarianceByEvent = "53"
    TAVarianceByPayGroup = "44"
    TAVarianceWithBudgets = "68"
    TAVarianceWithLabourStard = "79"
    TimesheetResultsSummary = "65"
    TotalHoursWorked = "11"
    UnapprovedClockings = "38"
    WeeklyTimesheet = "78"
    WorkRule = "29"
    #### Scheduling Reports ####
    


class ReportStatus(Enum):
    """Status of the report generation."""
    Processing = "Processing"
    Completed = "Completed"
    Viewed = "Viewed"


class ReportFormat(Enum):
    """File formats available for report downloads. These are used to select the file format in the dropdown menu."""
    PDF = "1"
    EXCEL = "2"
    DOC = "3"
    RTF = "4"
    CSV = "6"


class OrgUnit(Enum):
    """Organisation units available in the system (add more as necessary). These are used to select the checkbox of the org unit in the tree"""
    HolyCrossLaundry = "Holy Cross Laundry"


class ReportTab(Enum):
    """Report tabs available in the system. These are used to select the report tab at the top of the report page."""
    TimeAttendance = "#TimeAttendanceReport"
    Schedule = "#SchedulingReport"
    Reports = "#RequestPreview"

class OrgTemplate(Enum):
    """Create your own org template class using this class as a base class. You can get the values by right clicking and inspecting the element in the browser.
    Here is an example (Take note of "OrgTemplate" being passed in to the example class below.):

    class MyOrgTemplates(OrgTemplate):
        Example0 = "Example Text 0"
        Example1 = "Example Text 1"
    """

class JoelsOrgTemplates(OrgTemplate):
    HolyCrossLaundry = "Holy Cross Laundry"
    LaundyTransportCOS = "Laundry & Transport COS"