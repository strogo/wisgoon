package main

import (
  "fmt"
  "encoding/json"
  "net/http"
  "database/sql"
  _ "github.com/go-sql-driver/mysql"
  "gopkg.in/redis.v4"
  "strconv"
  "github.com/bradfitz/gomemcache/memcache"

)


type NotifCount struct {
	Status bool `json:"status"`
	Notif_count int `json:"notif_count"`
}

func main() {
	fmt.Println("application started")
	http.HandleFunc("/api/v6/notif/count/", apiNotifCount)
	http.ListenAndServe(":3000", nil)
}

func getUseridFromToken(token string) int{

	mc := memcache.New("127.0.0.1:11211")

	mkey := fmt.Sprintf("tuid_%s", token)
	value, err := mc.Get(mkey)
	if value != nil{
		userii, err := strconv.Atoi(string(value.Value))
		if err != nil {
			panic(err.Error())
		}
		return userii
	}

	db, err := sql.Open("mysql", "root:somaye@/feedreader")
    if err != nil {
        panic(err.Error())  // Just for example purpose. You should use proper error handling instead of panic
    }
    defer db.Close()

    stmtOut, err := db.Prepare("SELECT user_id FROM tastypie_apikey WHERE `key` = ?")
    if err != nil {
        panic(err.Error()) // proper error handling instead of panic in your app
    }
    defer stmtOut.Close()

    var userid int

    err = stmtOut.QueryRow(token).Scan(&userid) // WHERE number = 13
    if err != nil {
        panic(err.Error()) // proper error handling instead of panic in your app
    }
    useridstr := strconv.Itoa(userid)
    mc.Set(&memcache.Item{Key: mkey, Value: []byte(useridstr)})
    // mc.Set(&UserIDToken{Userid: userid})
	return userid
}

func apiNotifCount(w http.ResponseWriter, r *http.Request) {
	token := r.URL.Query().Get("token")
	fmt.Println(token)

	var userid int = getUseridFromToken(token)

    client := redis.NewClient(&redis.Options{
        Addr:     "localhost:6379",
        Password: "",
        DB:       0,
    })

    s := fmt.Sprintf("nc:01:%d", userid)

    ncc, err := client.Get(s).Result()
    if err != nil{
    	panic(err.Error())
    }

    nccint, err := strconv.Atoi(ncc)

	nc := &NotifCount{
		Status: true,
		Notif_count:nccint }

	js, _ := json.Marshal(nc)

	w.Header().Set("Content-Type", "application/json")
	w.Write(js)
}