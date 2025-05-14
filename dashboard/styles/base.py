"""
CSS styles for the AuditAI dashboard
"""
from abc import ABC, abstractmethod


class BaseStyles(ABC):
    """
    Abstract base class for dashboard styles.
    """
    
    @abstractmethod
    def get_css(self) -> str:
        """
        Get the CSS styles as a string.
        
        Returns:
            str: CSS styles
        """
        pass


class DashboardStyles(BaseStyles):
    """
    Main dashboard styles implementation.
    """
    
    def __init__(self, theme: str = "dark"):
        """
        Initialize dashboard styles.
        
        Args:
            theme: Theme name ('dark' or 'light')
        """
        self.theme = theme
        
    def get_css(self) -> str:
        """
        Get all CSS styles for the dashboard.
        
        Returns:
            str: Complete CSS styles
        """
        return f"""
        <style>
            {self._get_base_styles()}
            {self._get_header_styles()}
            {self._get_metrics_card_styles()}
            {self._get_chart_styles()}
            {self._get_tabs_styles()}
            {self._get_table_styles()}
            {self._get_misc_styles()}
        </style>
        """
    
    def _get_base_styles(self) -> str:
        """Base theme styles"""
        return """
        /* Base theme from original implementation */
        .main {
            background-color: #151528;
            color: #ffffff;
        }
        
        /* Typography */
        p, span, label, div {
            color: #ffffff !important;
        }
        
        h1, h2, h3, h4, h5, h6 {
            color: #ffffff !important;
            font-weight: 600;
        }
        
        /* Links */
        a {
            color: #4b78ff !important;
            text-decoration: none;
        }
        
        a:hover {
            text-decoration: underline;
            color: #759aff !important;
        }
        
        /* Containers */
        .stApp {
            background-color: #151528;
        }
        
        /* Fix for streamlit containers */
        div[data-testid="stVerticalBlock"] {
            gap: 15px !important;
        }
        
        /* Sidebar fixes - add these */
        [data-testid="stSidebar"] {
            background-color: #1e1e2f !important;
            border-right: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        [data-testid="stSidebar"] .stSelectbox label,
        [data-testid="stSidebar"] .stMultiSelect label {
            color: white !important;
        }
        
        [data-testid="stSidebar"] [data-testid="stMarkdown"] p {
            color: white !important;
        }
        
        [data-testid="stSidebar"] h1, 
        [data-testid="stSidebar"] h2, 
        [data-testid="stSidebar"] h3 {
            color: white !important;
        }
        
        /* Fix for selectbox in sidebar */
        [data-testid="stSidebar"] [data-baseweb="select"] {
            background-color: #151528;
        }
        
        [data-testid="stSidebar"] [data-baseweb="select"] > div {
            background-color: #151528;
            color: white;
        }
        """
        
    def _get_header_styles(self) -> str:
        """Header styles"""
        return """
        .header-title {
            font-size: 28px;
            font-weight: 700;
            margin-bottom: 25px;
            background: linear-gradient(90deg, #3a7bd5, #00d2ff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .header-subtitle {
            margin-bottom: 20px;
            max-width: 800px;
            line-height: 1.5;
        }
        """
        
    def _get_metrics_card_styles(self) -> str:
        """Metric card styles"""
        return """
        /* Enhanced metric cards */
        .metric-card {
            display: flex;
            padding: 18px;
            border-radius: 12px;
            background-color: #1e1e2f;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1), 0 1px 3px rgba(0,0,0,0.08);
            margin-bottom: 15px;
            transition: transform 0.2s, box-shadow 0.2s;
            height: 130px;
            overflow: hidden;
        }
        
        .metric-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 12px rgba(0,0,0,0.15), 0 2px 4px rgba(0,0,0,0.08);
        }
        
        .metric-icon {
            font-size: 24px;
            background-color: rgba(58, 123, 213, 0.1);
            border-radius: 50%;
            width: 48px;
            height: 48px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-right: 15px;
        }
        
        .primary-icon {
            background-color: rgba(58, 123, 213, 0.1);
        }
        
        .warning-icon {
            background-color: rgba(255, 177, 66, 0.1);
        }
        
        .danger-icon {
            background-color: rgba(255, 82, 82, 0.1);
        }
        
        .success-icon {
            background-color: rgba(46, 204, 113, 0.1);
        }
        
        .metric-content {
            flex: 1;
            display: flex;
            flex-direction: column;
        }
        
        .metric-title {
            font-size: 14px;
            color: white !important;
            margin-bottom: 8px;
            font-weight: 500;
        }
        
        .metric-value {
            font-size: 28px;
            font-weight: 700;
            color: white !important;
            margin-bottom: 6px;
        }
        
        .metric-trend {
            font-size: 12px;
            margin-top: 5px;
            font-weight: 500;
            color: white !important;
        }
        
        .metric-description {
            font-size: 11px;
            color: #B0B0B0 !important;
            margin-top: 5px;
        }
        
        .positive-metric {
            color: #4CAF50 !important;
        }
        
        .negative-metric {
            color: #F44336 !important;
        }
        
        .neutral-metric {
            color: #FFA500 !important;
        }
        
        /* Progress bar for resource metrics */
        .metric-progress-container {
            width: 100%;
            height: 8px;
            background-color: rgba(255,255,255,0.1);
            border-radius: 4px;
            margin-top: 10px;
            overflow: hidden;
        }
        
        .metric-progress-bar {
            height: 100%;
            background: linear-gradient(90deg, #3a7bd5, #00d2ff);
            border-radius: 4px;
        }
        
        .positive-trend {
            color: #4CAF50 !important;
        }
        
        .negative-trend {
            color: #F44336 !important;
        }
        """
        
    def _get_chart_styles(self) -> str:
        """Chart styles"""
        return """
        /* Chart container styles */
        .chart-container {
            background-color: #1e1e2f;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 20px;
        }
        
        /* Fix for tooltips/hover visibility */
        .st-emotion-cache-1vbkxwb g, .st-emotion-cache-1vbkxwb rect {
            pointer-events: auto !important;
        }
        
        /* Ensure tooltip visibility */
        .st-emotion-cache-zr28e8 {
            visibility: visible !important;
            opacity: 1 !important;
            z-index: 9999 !important;
        }
        
        /* Additional chart styles from src version */
        .stChart {
            background-color: rgba(30, 30, 47, 0.5);
            border-radius: 8px;
            padding-top: 10px;
        }
        
        /* Chart overlay for better hover detection */
        .st-emotion-cache-13ejsyy:hover div[data-testid="stTooltip"] {
            visibility: visible !important;
            opacity: 1 !important;
            z-index: 1000 !important;
        }
        """
        
    def _get_tabs_styles(self) -> str:
        """Tab styles"""
        return """
        /* Tab styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
        }
        
        .stTabs [data-baseweb="tab"] {
            background-color: #1e1e2f;
            border-radius: 6px 6px 0 0;
            padding: 8px 16px;
            border: none;
            color: white !important;
        }
        
        .stTabs [aria-selected="true"] {
            background-color: #3a7bd5 !important;
            color: white !important;
        }
        
        /* Fix for the tabs */
        button[role="tab"] {
            color: white !important;
        }
        """
        
    def _get_table_styles(self) -> str:
        """Table styles"""
        return """
        /* Better dataframe styling */
        [data-testid="stDataFrame"] {
            background-color: #1e1e2f !important;
            border-radius: 12px;
            padding: 5px;
            margin-bottom: 20px;
        }
        
        [data-testid="stDataFrame"] table {
            border-collapse: collapse;
        }
        
        [data-testid="stDataFrame"] th {
            background-color: rgba(58, 123, 213, 0.1);
            color: #3a7bd5 !important;
        }
        
        [data-testid="stDataFrame"] td {
            border-bottom: 1px solid rgba(255,255,255,0.05);
        }
        
        /* Model comparison table */
        .model-comparison-table {
            margin-top: 15px;
            margin-bottom: 25px;
        }
        
        .model-comparison-table table {
            width: 100%;
            border-collapse: collapse;
        }
        
        .model-comparison-table th {
            text-align: left;
            padding: 12px 15px;
            font-weight: 500;
            color: #B0B0B0 !important;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }
        
        .model-comparison-table td {
            padding: 15px 15px;
            border-bottom: 1px solid rgba(255,255,255,0.05);
            color: white !important;
        }
        
        .bar-container {
            position: relative;
            height: 10px;
            background-color: rgba(255,255,255,0.1);
            border-radius: 5px;
            margin-bottom: 5px;
        }
        
        .bar-fill {
            position: absolute;
            top: 0;
            left: 0;
            height: 100%;
            background: linear-gradient(90deg, #3a7bd5, #00d2ff);
            border-radius: 5px;
        }
        
        .bar-container span {
            display: block;
            font-size: 12px;
            margin-top: 12px;
            color: white !important;
        }
        """
        
    def _get_misc_styles(self) -> str:
        """Miscellaneous styles"""
        return """
        /* Better selectbox styling */
        [data-testid="stSelectbox"] {
            background-color: #1e1e2f;
            border-radius: 8px;
            margin-bottom: 10px;
            color: white;
        }
        
        .stSelectbox label {
            color: white !important;
        }
        
        /* Better slider styling */
        [data-testid="stSlider"] > div {
            background-color: #1e1e2f;
            border-radius: 8px;
            padding: 10px;
            margin-bottom: 10px;
        }
        
        [data-testid="stSlider"] > div > div > div > div {
            background-color: #3a7bd5;
        }
        
        /* Expander styling */
        .streamlit-expanderHeader {
            background-color: #1e1e2f;
            border-radius: 8px;
            font-weight: 500;
            color: white !important;
        }
        
        .streamlit-expanderContent {
            background-color: #1e1e2f;
            border-radius: 0 0 8px 8px;
        }
        
        /* === Global Dropdown Visibility Fix === */
        ul[role="listbox"] {
            background-color: #1e1e2f !important;
            border-radius: 8px !important;
        }
        li[role="option"] {
            background-color: #1e1e2f !important;
            color: #ffffff !important;
        }
        li[role="option"][aria-selected="true"],
        li[role="option"]:hover {
            background-color: #2a2a45 !important;
            color: #ffffff !important;
        }
        
        /* Fix Reset button styling */
        [data-testid="stSidebar"] div.stButton > button {
            background-color: #d14343 !important;
            color: #ffffff !important;
            border: 1px solid #d14343 !important;
        }
        
        /* Reset button styling */
        [data-testid="stSidebar"] button {
            background-color: #d14343 !important;
            color: #ffffff !important;
            border: 1px solid #d14343 !important;
        }
        """


class LightThemeStyles(DashboardStyles):
    """
    Light theme implementation for dashboard.
    """
    
    def __init__(self):
        """Initialize light theme styles"""
        super().__init__(theme="light")
    
    def _get_base_styles(self) -> str:
        """Override base styles for light theme"""
        return """
        .main {
            background-color: #ffffff;
            color: #333333;
        }
        
        p, span, label, div, h1, h2, h3, h4, h5, h6 {
            color: #333333 !important;
        }
        
        .section-header {
            font-size: 22px;
            font-weight: 600;
            margin: 30px 0 15px 0;
            border-left: 5px solid #3a7bd5;
            padding-left: 10px;
            color: #333333 !important;
        }
        """
    def _get_chart_styles(self) -> str:
        """Chart styles"""
        return """
        /* Chart container styling */
        .chart-container {
            background-color: #1e1e2f;
            border-radius: 12px;
            padding: 15px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        
        /* Fix chart text */
        .js-plotly-plot text {
            fill: white !important;
        }
        
        /* Fix hover visibility issues */
        .js-plotly-plot .hovertext,
        .js-plotly-plot .hovertext text {
            visibility: visible !important;
            opacity: 1 !important;
            z-index: 1000 !important;
        }
        
        /* Ensure tooltips are visible */
        .js-plotly-plot .plotly .hover,
        .js-plotly-plot .plotly .hover-bg,
        .js-plotly-plot .plotly:hover .hover-bg,
        .js-plotly-plot .plotly:hover .hover {
            pointer-events: all !important;
            visibility: visible !important;
        }
        
        /* Fix for axis titles and labels */
        .xtitle, .ytitle, .gtitle {
            fill: white !important;
        }
        
        .xtick text, .ytick text {
            fill: white !important;
        }
        
        /* Fix for legend text */
        .legendtext {
            fill: white !important;
        }
        
        .chart-description {
            margin-bottom: 15px;
            color: #B0B0B0 !important;
            font-size: 14px;
        }
        
        /* Ensure tooltip stays visible */
        .plotly-tooltip {
            z-index: 1000 !important;
            visibility: visible !important;
            opacity: 1 !important;
            background-color: rgba(30, 30, 47, 0.9) !important;
        }
        
        /* Force Streamlit tooltip visibility */
        [data-testid="stTooltip"] {
            opacity: 1 !important;
            visibility: visible !important;
        }
        """