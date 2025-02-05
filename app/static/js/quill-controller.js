class QuillNotesManager {

    intervalStart(){
        
        clearTimeout(this.timeout)
        self = this
        this.timeout = setTimeout(() => {
            self.saveChanges()
        }, 500);
    }

    saveChanges(){
        let url = window.location.href;
        let data = {
            "note_id": note_id,
            "assessment_id": assessment_id,
            "category_order": category_order,
            "note_content": quill.getContents()
        };
        fetch(url, {
            "method": "PUT",
            "headers": {
                "Authorization": window.localStorage.getItem("access_token"),
                "HX-Request":"true",
                "Content-Type":"application/json"
            },
            "body": JSON.stringify(data)
        }).then((response)=>{
            var saveResponse = response;
        })
    }
}
