import { $api, ENDPOINTS } from "./api"

enum METHOD {
	GET = "GET",
	POST = "POST"
}
interface IAPIRequest {
	url: string,
	method: string,
	data?: {}
}
export const APIRequest = async (api_data: IAPIRequest) => {
	try {
		if (api_data.method === "POST") {
			const request = await $api.post(api_data.url, {
				data: api_data.data
			})

			return request
		} else {
			const response = await $api.get(api_data.url)
			const data = await response.data

			return data
		}

		// return data
	} catch (error: any) {
		console.error(error.response.data)
	}
}