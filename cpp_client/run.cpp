#include "phenoaiclient.hpp"

// Compile with the -lcurl flag

int main(){

	PhenoAIClient client("127.0.0.1", 8081);
	float data[3] = {1.5, 0.0, 1.0};
	nlohmann::json result = client.predict_values(data, 3, true);
	std::cout << result.dump(4) << std::endl;

	return 0;
}
