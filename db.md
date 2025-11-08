erDiagram
	direction TB
	USER {
		int id PK ""  
		string full_name  ""  
		string email  ""  
		string phone  ""  
		date date_of_birth  ""  
		string profile_image  ""  
		datetime registration_date  ""  
		string status  ""  
	}
	ACCOUNT {
		int id PK ""  
		int user_id FK ""  
		string usename  ""  
		string password  ""  
		string role  ""  
		string status  ""  
	}
	DESTINATION {
		int destination_id PK ""  
		int company_id FK ""  
		string destination_name  ""  
		string location_address  ""  
		decimal latitude  ""  
		decimal longitude  ""  
		string destination_type  ""  
		int popularity_score  ""  
		int avg_duration  ""  
		datetime created_date  ""  
		datetime updated_date  ""  
		boolean is_active  ""  
	}
	DESTINATION_CATEGORY {
		int category_id PK ""  
		string category_name  ""  
		text category_description  ""  
		string icon  ""  
	}
	DESTINATION_CATEGORY_MAPPING {
		int mapping_id PK ""  
		int destination_id FK ""  
		int category_id FK ""  
	}
	DESTINATION_ATTRIBUTE {
		int attribute_id PK ""  
		int destination_id FK ""  
		string attribute_key  ""  
		string attribute_value  ""  
		string attribute_type  ""  
	}
	DESTINATION_DESCRIPTION {
		int description_id PK ""  
		int destination_id FK ""  
		string language_code  ""  
		string title  ""  
		text short_description  ""  
		text full_description  ""  
		text history_info  ""  
		text cultural_info  ""  
		text travel_tips  ""  
		datetime created_date  ""  
		datetime updated_date  ""  
	}
	ITINERARY {
		int itinerary_id PK ""  
		int user_id FK ""  
		int user_type_id FK ""  
		int trend_id FK ""  
		string itinerary_name  ""  
		date start_date  ""  
		date end_date  ""  
		int total_days  ""  
		int total_destinations  ""  
		string status  ""  
		datetime created_date  ""  
		datetime updated_date  ""  
	}
	ITINERARY_DESTINATION {
		int itinerary_dest_id PK ""  
		int itinerary_id FK ""  
		int destination_id FK ""  
		int day_number  ""  
		int visit_order  ""  
		time start_time  ""  
		time end_time  ""  
		int duration_minutes  ""  
		text notes  ""  
	}
	COMPANY {
		int company_id PK ""  
		string company_name  ""  
		string address  ""  
		string phone  ""  
		string email  ""  
		string website  ""  
		datetime registration_date  ""  
		string status  ""  
	}