function tokenLoginCheck(){

    if( window.localStorage.getItem("access_token") ){
        let headers = new Headers();
        headers.append("Authorization", window.localStorage.getItem("access_token") );
        fetch(tokenCheckUrl, {
                "method": 'GET',
                "headers": headers
                }
             ).then(
                 response => response.json()
                 ).then(data => {
                     window.location.href = data.redirect_to;
                     }).catch((error)=>{
                         console.log('Error:', error);
                         })
    }
}

setTimeout(()=>{tokenLoginCheck()}, 500)

/*
   ( () => {

   let headers = new Headers().

   headers.append("Authorization", window.localStorage.getItem("access_token") )

   fetch(tokenCheckUrl, {
method: 'GET',

})
.then(response => response.json())
.then(data => {
console.log('Success:', data);
})
.catch((error)=>{
console.log('Error:', error);
})

})();
 */
