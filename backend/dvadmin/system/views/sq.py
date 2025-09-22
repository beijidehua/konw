
let db = SQLiteDB.sharedInstance

let result = db.query(sql: "SELECT sql FROM sqlite_master WHERE type=\"table\" AND name = \"t_user\"")
print("---查询结果---\n\(result)")
print("---建表SQL---\n\(result[0]["sql"]!)")