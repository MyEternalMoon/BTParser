numbers = [b'0',b'1', b'2', b'3', b'4', b'5', b'6', b'7',b'8',b'9',b'0']


class BTParseException(Exception):
	def __init__(self, info):
		self.info = info

	def __str__(self):
		return self.info


class BTParser:
	def __init__(self):

		self.message = None
		self.announce = ''
		self.announce_list = []
		self.creatation_date = None
		self.comment = ''
		self.creator = ''
		self.length = ''
		self.name = ''
		self.stream = None

	def parse(self, path:str):
		try:
			with open(path, 'rb') as f:
				self.message = self.parseNext()
		except BTParseException as e:
			print("Some error happens when read the bt source:\n"+e)
		else:
			pass

	def parseNext(self):
		tmp = self.stream.readByte()
		# start with integer->string
		if tmp in numbers:
			return self.parseString(int(tmp))
		elif tmp == b'i':
			return self.parseInteger()
		elif tmp == b'd':
			return self.parseDictionary()
		elif tmp == b'l':
			return self.parseList()
		else:
			raise BTParseException(f"Invalid byte:{str(tmp)}, not any allowed types in bencode")


	def parseInteger(self)->int:
		"""
		BT种子的数字结构:i....e
		可以以负号开头，以0开头的数字非法, -0非法
		:return: 解析得到的数字结果
		"""
		tmp = b''
		zero_not_allowed = False # 读到0是否仍然允许，刚开始什么都没有，可以读到0
		while True:
			cur_byte = self.stream.readByte()
			if cur_byte in numbers: # 读到了数字，不过还要检查一下
				if cur_byte == b'0' and zero_not_allowed: # 读到0了，但是不允许读到0
					raise BTParseException("Invalid integer format.")
				elif cur_byte == b'0' and len(tmp) == 0: # 当总长度为0，可以读到0，但不能允许下一个0了
					zero_not_allowed = True
				zero_not_allowed = False # 读到其他数字， 允许继续读到0
				tmp += cur_byte
			elif cur_byte == b'-' and len(tmp) == 0:
				zero_not_allowed = True
				tmp += cur_byte
			elif cur_byte == b'e':
				return int(tmp)
			else:
				raise BTParseException(f"Invalid byte '{str(tmp)}' when parsing integer.")

	def parseString(self, length:int)->str:
		"""
		BT种子的字符串结构int:....., 冒号后跟一个长度为int大小的串，估计都是ascii编码的，不然我读byte就坏了
		:param length: 长度
		:return: 解析得到的字符串
		"""
		tmp = b''
		if self.stream.readByte() != b':':
			raise BTParseException(f"Invalid byte '{str(tmp)}' when parsing string, ':' needed.")
		for i in range(length):
			tmp += self.stream.readByte()
		return str(tmp)

	def parseDictionary(self)->dict:
		"""
		散列表的key一定是一个字符串
		:return:
		"""
		ret = dict()
		tmp = b''
		while True:
			tmp = self.stream.readByte()
			if tmp == b'e': # dictionary is over
				return ret
			elif tmp not in numbers: #error happens when key is not a string
				raise BTParseException("Invalid key when parsing dictionary, a key must be a string")
			key = self.parseString(int(tmp))
			value = self.parseNext()
			ret[key] = value


	def parseList(self)->list:
		pass
