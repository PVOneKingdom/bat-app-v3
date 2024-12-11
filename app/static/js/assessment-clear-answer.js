setTimeout(() => {
    console.log("this triggered");
    document.querySelector("#clear-answer-button").addEventListener("click", (e)=>{
        e.preventDefault();
        let radios = document.querySelectorAll("#answer-value-wrapper input");
        radios.forEach((element)=>{
            element.checked = false;
        })
    });
}, 200);
