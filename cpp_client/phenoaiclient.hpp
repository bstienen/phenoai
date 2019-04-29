#ifndef BSMAI_CLIENT
#define BSMAI_CLIENT

#include <iostream>
#include <sstream>
#include <fstream>
#include <curl/curl.h>
#include "json.hpp"


class PhenoAIClient{
private:
	std::string _server_ip;
	int _server_port;
	CURL* _curl;
public:
	// Constructor
	PhenoAIClient(std::string ip, int port){
		// Store server settings
		set_server_ip(ip);
		set_server_port(port);
		// Create curl handle
		curl_global_init(CURL_GLOBAL_ALL);
		_curl = curl_easy_init();
	}
	// Destructor
	~PhenoAIClient(){ curl_global_cleanup(); }

	// Getters and setters
	std::string get_server_ip(){ return _server_ip; }
	int get_server_port(){ return _server_port; }
	void set_server_ip(std::string ip){ _server_ip = ip; }
	void set_server_port(int port){ _server_port = port; }

	// Predict functions
	nlohmann::json predict_values(float data[], int nParameters, bool mapping){
		// Translate data array to python format list
		std::string datalist = "[";
		for(int i=0; i<nParameters; ++i){
			if(datalist != "["){
				datalist += ",";
			}
			std::ostringstream buff;
		    buff << data[i];
			datalist += buff.str(); 
		}
		datalist += "]";

		// Query server
		std::string result = query("values", datalist, mapping);

		// Convert result into json object
		return resultConstructor(result);
	}
	nlohmann::json predict_file(const char* filepath, bool mapping){
		// Translate data array to python format list
		std::ifstream ifs(filepath);
		std::string content( (std::istreambuf_iterator<char>(ifs) ),
							 (std::istreambuf_iterator<char>() ) );
		// Query server
		std::string result = query("file", content, mapping);

		// Convert result into json object
		return resultConstructor(result);
	}


	// Send request
	std::string query(std::string mode, std::string data, bool mapping){
		// Create post request
		std::string mapping_str = (mapping)?"1":"0";
		std::string poststring = "get_results_as_string=1&mode="+mode+"&data="+data+"&mapping="+mapping_str+"";

		std::string readBuffer;
		// Check if curl handle exists
		if (_curl){

			// Allocate space for result code
			CURLcode res;

			// First set the URL that is about the receive our POST. This URL can
			// just as well be a https:// URL if that is what should receive the data 
			curl_easy_setopt(_curl, CURLOPT_URL, _server_ip.c_str());
			curl_easy_setopt(_curl, CURLOPT_PORT, _server_port);
			curl_easy_setopt(_curl, CURLOPT_WRITEFUNCTION, WriteCallback);
			curl_easy_setopt(_curl, CURLOPT_WRITEDATA, &readBuffer);
			// New specify the POST data 
			curl_easy_setopt(_curl, CURLOPT_POSTFIELDS, poststring.c_str());

			// Perform the request, res will get the return code 
			res = curl_easy_perform(_curl);
			// Check for errors 
			if(res != CURLE_OK){
				std::cout << "curl_easy_perform() failed: " << curl_easy_strerror(res) << std::endl; 
			}

			// Always cleanup 
			curl_easy_cleanup(_curl);

		}
		return readBuffer;
	}

	// Result constructor
	nlohmann::json resultConstructor(std::string result){
		auto jsonresult = nlohmann::json::parse(result);
		if(jsonresult["status"] == "error"){
			std::string errortype = jsonresult["type"];
			std::string errormessage = jsonresult["message"];
			std::string error = errormessage+" ("+errortype+")";
			throw std::runtime_error(error);
		}
		return jsonresult;
	}

	static size_t WriteCallback(void *contents, size_t size, size_t nmemb, void* userp){
		((std::string*)userp)->append((char*)contents, size * nmemb);
		return size*nmemb;
	}
	
};

#endif
