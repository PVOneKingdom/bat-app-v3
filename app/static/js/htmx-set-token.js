document.addEventListener("htmx:configRequest", (e)=>{
    const token = window.localStorage.getItem("access_token");
    e.detail.headers["Authorization"] = token;
});
