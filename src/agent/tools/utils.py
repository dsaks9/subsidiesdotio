from src.agent.tools.subsidy_report_parameters import REGIONS, STATUS

def check_regions(regions):
    if regions is not None:
        invalid_regions = [region for region in regions if region not in REGIONS]
        if invalid_regions:
            return None
    return regions