// Please note that the code below is automatically generated and may be
// incomplete or redundant. Please make sure to verify these class
// specifications and apply proper changes to lines marked by comments.
//
// Thanks for using json2code!


// generated from config file: photo.json which was generated from json file: photo.json
class Photo {
	var fileName: String?
	var id: Int?

	class func fromJson(json: JSON) -> Photo {
		var newObject = Photo()
		newObject.fileName = json["file_name"].stringValue
		newObject.id = json["id"].intValue
		return newObject
	}

	func toJson() -> JSON {
		var json: JSON = JSON([String: AnyObject]())
		json["file_name"].stringValue = self.fileName
		json["id"].intValue = self.id
		return json
	}
}

// generated from config file: post.json which was generated from json file: post.json
class Post {
	var body: String?
	var userId: Int?
	var title: String?
	var id: Int?

	class func fromJson(json: JSON) -> Post {
		var newObject = Post()
		newObject.body = json["body"].stringValue
		newObject.userId = json["user_id"].intValue
		newObject.title = json["title"].stringValue
		newObject.id = json["id"].intValue
		return newObject
	}

	func toJson() -> JSON {
		var json: JSON = JSON([String: AnyObject]())
		json["body"].stringValue = self.body
		json["user_id"].intValue = self.userId
		json["title"].stringValue = self.title
		json["id"].intValue = self.id
		return json
	}
}

// generated from config file: post_stubs.json which was generated from json file: user.json
class PostStubs {
	var likes: Int?
	var title: String?

	class func fromJson(json: JSON) -> PostStubs {
		var newObject = PostStubs()
		newObject.likes = json["likes"].intValue
		newObject.title = json["title"].stringValue
		return newObject
	}

	func toJson() -> JSON {
		var json: JSON = JSON([String: AnyObject]())
		json["likes"].intValue = self.likes
		json["title"].stringValue = self.title
		return json
	}
}

// generated from config file: profile_photo.json which was generated from json file: user.json
class ProfilePhoto {
	var fileName: String?
	var id: Int?

	class func fromJson(json: JSON) -> ProfilePhoto {
		var newObject = ProfilePhoto()
		newObject.fileName = json["file_name"].stringValue
		newObject.id = json["id"].intValue
		return newObject
	}

	func toJson() -> JSON {
		var json: JSON = JSON([String: AnyObject]())
		json["file_name"].stringValue = self.fileName
		json["id"].intValue = self.id
		return json
	}
}

// generated from config file: user.json which was generated from json file: user.json
class User {
	var firstName: String?
	var lastName: String?
	var postUris: String?
	var postStubs: [Post?]	// or PostStubs? - please choose appropriate type
	var profilePhoto: Photo?	// or ProfilePhoto? - please choose appropriate type
	var id: Int?

	class func fromJson(json: JSON) -> User {
		var newObject = User()
		newObject.firstName = json["first_name"].stringValue
		newObject.lastName = json["last_name"].stringValue
		newObject.postUris = []
		for subJson in json["post_uris"] {
			newObject.postUris.append(subJson["post_uris"].stringValue)

		}
		newObject.postStubs = []
		for subJson in json["post_stubs"] {
			newObject.postStubs.append(Post.fromJson(subJson["post_stubs"]!)) 	// or PostStubs - please choose appropriate conversion
		}
		newObject.profilePhoto = Photo.fromJson(json["profile_photo"]!)	// or ProfilePhoto - please choose appropriate conversion
		newObject.id = json["id"].intValue
		return newObject
	}

	func toJson() -> JSON {
		var json: JSON = JSON([String: AnyObject]())
		json["first_name"].stringValue = self.firstName
		json["last_name"].stringValue = self.lastName
		json["post_uris"].arrayValue = self.postUris
		var postStubsArray = [JSON]()
		for obj in self.postStubs {
			 postStubsArray.append(obj.toJson())
		}
		json["post_stubs"] = postStubsArray
		json["profile_photo"] = self.profilePhoto.toJson()
		json["id"].intValue = self.id
		return json
	}
}

