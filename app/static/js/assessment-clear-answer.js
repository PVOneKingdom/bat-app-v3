setTimeout(() => {
        document.querySelector("#clear-answer-button").addEventListener("click", (e)=>{
                e.preventDefault();
                document.querySelectorAll(".answer-value-wrapper").forEach((element)=>{
                            element.checked = false;
                        })
                });
        }, 200);
