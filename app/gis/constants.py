RUBRICS_FILE_POSSIBLE_KEYS = {
    "rubrics_file",
    "rubric_file",
}
RUBRICS_CODES_POSSIBLE_KEYS = {
    "rubrics_codes",
    "rubric_codes",
    "rubrics_ids",
    "rubric_ids",
}

CITIES_FILE_POSSIBLE_KEYS = {
    "cities_file",
    "city_file",
}
CITIES_IDS_POSSIBLE_KEYS = {
    "cities_ids",
    "city_ids",
    "cities_codes",
    "city_codes",
}

PARSE_REVIEWS_POSSIBLE_KEYS = {
    "parse_reviews",
}

PARSE_MENUS_POSSIBLE_KEYS = {
    "parse_menus",
}

PARSE_MEDIA_POSSIBLE_KEYS = {
    "parse_media",
}

CONFLICTING_KEYS = {
    "rubrics": RUBRICS_FILE_POSSIBLE_KEYS.union(RUBRICS_CODES_POSSIBLE_KEYS).union(
        {"parse_all_rubrics"}
    ),
    "cities": CITIES_FILE_POSSIBLE_KEYS.union(CITIES_IDS_POSSIBLE_KEYS).union(
        {"country", "parse_all_cities"}
    ),
    "parse_reviews": PARSE_REVIEWS_POSSIBLE_KEYS,
    "parse_menus": PARSE_MENUS_POSSIBLE_KEYS,
    "parse_media": PARSE_MEDIA_POSSIBLE_KEYS,
}


TRUE_VARIATIONS = {"true", "1", "yes", "y", "t"}


FIELDS = [
    "items.locale",
    "items.flags",
    "items.search_attributes.detection_type",
    "items.search_attributes.additional_info",
    "items.search_attributes.best_keyword",
    "search_attributes",
    "items.search_attributes.relevance",
    "items.search_attributes.personal_priority",
    "items.search_attributes.dgis_source_type",
    "items.search_attributes.dgis_found_by_address",
    "items.search_attributes.dgis_ad_type",
    "items.search_attributes.dgis_ad_rubric_id",
    "items.search_attributes.detection_type",
    "items.adm_div",
    "items.city_alias",
    "items.region_id",
    "items.segment_id",
    "items.reviews",
    "items.point",
    "request_type",
    "context_rubrics",
    "query_context",
    "items.links",
    "items.name_ex",
    "items.name_back",
    "items.org",
    "items.group",
    "items.dates",
    "items.external_content",
    "items.contact_groups",
    "items.comment",
    "items.ads.options",
    "items.email_for_sending.allowed",
    "items.stat",
    "items.stop_factors",
    "items.description",
    "items.geometry.centroid",
    "items.geometry.selection",
    "items.geometry.style",
    "items.timezone_offset",
    "items.context",
    "items.level_count",
    "items.address",
    "items.is_paid",
    "items.access",
    "items.access_comment",
    "items.for_trucks",
    "items.is_incentive",
    "items.paving_type",
    "items.capacity",
    "items.schedule",
    "items.schedule_special",
    "items.floors",
    "items.floor_id",
    "items.floor_plans",
    "dym",
    "ad",
    "items.rubrics",
    "items.routes",
    "items.platforms",
    "items.directions",
    "items.barrier",
    "items.reply_rate",
    "items.purpose",
    "items.purpose_code",
    "items.attribute_groups",
    "items.route_logo",
    "items.has_goods",
    "items.has_apartments_info",
    "items.has_pinned_goods",
    "items.has_realty",
    "items.has_otello_stories",
    "items.has_exchange",
    "items.has_payments",
    "items.has_dynamic_congestion",
    "items.is_promoted",
    "items.congestion",
    "items.delivery",
    "items.order_with_cart",
    "search_type",
    "items.has_discount",
    "items.metarubrics",
    "items.subtype",
    "items.detailed_subtype",
    "items.temporary_unavailable_atm_services",
    "items.poi_category",
    "items.has_ads_model",
    "items.vacancies",
    "items.structure_info.material",
    "items.structure_info.floor_type",
    "items.structure_info.gas_type",
    "items.structure_info.year_of_construction",
    "items.structure_info.elevators_count",
    "items.structure_info.is_in_emergency_state",
    "items.structure_info.project_type",
    "items.has_otello_hotels",
    "items.ski_lift",
    "items.ski_track",
    "items.inactive",
]

RUBRICS_WITH_PRICE_TAB = {
    "178",
    "305",
    "652",
    "5603",
    "382",
    "651",
    "110355",
    "58858",
    "20165",
    "13102",
    "13726",
    "56759",
    "14942",
    "69989",
    "13597",
    "51009",
    "53986",
    "70190",
    "67142",
    "50870",
    "110479",
    "110353",
    "110351",
    "110352",
    "69491",
    "110975",
    "110998",
    "405",
    "7689",
    "205",
}
RUBRICS_WITH_MENU_TAB = {
    "161",
    "164",
    "159",
    "1203",
    "9786",
    "21501",
    "58871",
    "110317",
    "110408",
    "165",
    "162",
    "110411",
    "51459",
    "110376",
    "52248",
    "166",
    "15791",
    "111593",
    "363",
    "469",
    "879",
    "10803",
    "111594",
    "112656",
    "112658",
    "21387",
    "558",
    "16677",
}


URL_TEMPLATE = (
    "https://catalog.api.2gis.ru/2.0/catalog/branch/list"
    "?page={page}"
    "&page_size={per_page}"
    "&rubric_id={rubric_id}"
    "&region_id={city_id}"
    "&locale=ru_RU"
    f"&fields={','.join(FIELDS)}"
    "&key=rutnpt3272"
)
REVIEWS_URL_TEMPLATE = "https://public-api.reviews.2gis.com/3.0/branches/{org_id}/reviews?limit={per_page}&offset={offset}&is_advertiser=false&fields=meta.providers,meta.branch_rating,meta.branch_reviews_count,meta.total_count,reviews.hiding_reason,reviews.emojis,reviews.trust_factors&without_my_first_review=false&rated=true&sort_by=friends&key=6e7e1929-4ea9-4a5d-8c05-d601860389bd&locale=ru_RU"
MENUS_URL_TEMPLATE = "https://market-backend.api.2gis.ru/5.0/product/items_by_branch?branch_id={org_id}&locale=ru_RU&page={page}&page_size={per_page}&feature_config=categories_without_fake_first_level,range_price_type_supported,from_price_type_supported,fas_not_ad_text"
MEDIA_URL_TEMPLATE = "https://api.photo.2gis.com/3.0/objects/{org_id}/albums/{album_type}/media?key=gYu1s9N1wP&page_size={per_page}&locale=ru_RU"
