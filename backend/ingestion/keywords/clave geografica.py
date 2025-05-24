def main(client):
    gtc_service = client.get_service("GeoTargetConstantService")

    gtc_request = client.get_type("SuggestGeoTargetConstantsRequest")

    gtc_request.locale = LOCALE
    gtc_request.country_code = COUNTRY_CODE

    # The location names to get suggested geo target constants.
    gtc_request.location_names.names.extend(
        ["Paris", "Quebec", "Spain", "Deutschland"]
    )

    results = gtc_service.suggest_geo_target_constants(gtc_request)

    for suggestion in results.geo_target_constant_suggestions:
        geo_target_constant = suggestion.geo_target_constant
        print(
            f"{geo_target_constant.resource_name} "
            f"({geo_target_constant.name}, "
            f"{geo_target_constant.country_code}, "
            f"{geo_target_constant.target_type}, "
            f"{geo_target_constant.status.name}) "
            f"is found in locale ({suggestion.locale}) "
            f"with reach ({suggestion.reach}) "
            f"from search term ({suggestion.search_term})."
        )
      