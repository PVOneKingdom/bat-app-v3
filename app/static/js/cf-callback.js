if(typeof(cfCallback) != "function"){
    window.cfCallback = (token) => {
        let field = document.querySelector(".cf-turnstile-token-field");
        field.value = token;
    }
}
