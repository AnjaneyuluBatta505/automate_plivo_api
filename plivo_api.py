import requests


class Error(Exception):
	pass


class PlivoAPI(object):

	def __init__(self, auth_id, auth_token):
		self.auth_id = auth_id
		self.auth_token = auth_token
		self.base_url = 'https://api.plivo.com/v1'
		self.initial_cash_credits = self.get_acc_cash_credits()

	@property
	def auth_headers(self):
		return requests.auth.HTTPBasicAuth(self.auth_id, self.auth_token)

	def post(self, uri, data={}, headers={}):
		headers_info = {'Content-type': 'application/json'}
		if headers:
			headers_info.extend(headers)
		return requests.post(uri, json=data, headers=headers_info, auth=self.auth_headers)

	def get(self, uri, data={}):
		headers_info = {'Content-type': 'application/json'}
		return requests.get(uri, params=data, headers=headers_info, auth=self.auth_headers)

	def raise_error(self, uri, response):
		resp_data = response.json()
		err_msg = 'uri: {uri} Status Code: {status}, error: {error}'.format(
			uri = uri,
			status=response.status_code,
			error=resp_data.get('error')
		)
		raise Error(err_msg)

	def get_outbound_pricing(self):
		uri = '{base_url}/v1/Account/{auth_id}/Pricing/'.format(
			base_url=self.base_url, auth_id=self.auth_id
		)
		response = self.get(uri)
		resp_data = response.json()
		if 'error' in resp_data:
			return self.raise_error(uri, response)
		else:
			return float(resp_data['message']['outbound']['rate'])

	def get_acc_cash_credits(self):
		uri = '{base_url}/Account/{auth_id}/'.format(
			base_url=self.base_url, auth_id=self.auth_id
		)
		response = self.get(uri)
		resp_data = response.json()
		if 'error' in resp_data:
			return self.raise_error(uri, response)
		else:
			return float(resp_data['cash_credits'])


	def handle_success_message(self, message_uuid):
		uri = '{base_url}/Account/{auth_id}/Message/{message_uuid}/'.format(
			base_url=self.base_url, auth_id=self.auth_id, message_uuid=message_uuid
		)
		response = self.get(uri)
		resp_data = response.json()
		if 'error' in resp_data:
			return self.raise_error(uri, response)
		else:
			outbound_price = self.get_outbound_pricing()
			total_rate = float(resp_data['total_rate'])
			assert outbound_price == total_rate
			cash_credits = self.get_acc_cash_credits()
			assert cash_credits == (self.initial_cash_credits - total_rate)
			return True

	def get_message_uuid(self, src, dst, txt, mtype='sms', **kwargs):
		uri = '{base_url}/Account/{auth_id}/Message/'.format(
			base_url=self.base_url, auth_id=self.auth_id
		)
		data = {'src': src, 'dst': dst, 'text': txt, 'type': mtype}

		if kwargs.get('url'):
			data['url'] = kwargs.get('url')
		if kwargs.get('method'):
			data['method'] = kwargs.get('method')
		if kwargs.get('log'):
			data['log'] = kwargs.get('log')

		response = self.post(uri, data)
		resp_data = response.json()
		if 'error' in resp_data:
			return self.raise_error(uri, response)
		else:
			message_uuid = resp_data.get('message_uuid')
			message_uuid = message_uuid[0] if isinstance(message_uuid, list) else message_uuid
			return message_uuid


	def send_message(self, *args, **kwargs):
		message_uuid = self.get_message_uuid(*args, **kwargs)
		return self.handle_success_message(message_uuid)


if __name__ == '__main__':
	auth_id = 'SAMDA0MWZLYZFHNTEWNT'
	auth_token = 'YjUzODc2NzM5MmU2M2E3OTYzMjY0NjBjY2U1Yzg5'
	api = PlivoAPI(auth_id, auth_token)
	src = '14153014770'
	dst = '14153014785'
	txt = 'Hello world'
	if api.send_message(src, dst, txt):
		print("Message processed")
	else:
		print("Message processing failed")
