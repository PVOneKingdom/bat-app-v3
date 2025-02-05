
setTimeout(() => {
    window.quillController = new QuillNotesManager()
    window.quill = new Quill("#note-quill",
        {
            "theme":"snow",
            "placeholder":"Your notes goes here...",
            "modules": {
                "toolbar": [
                    ["bold", "italic", "underline", "strike"],
                    [{"list": "ordered"},{"list": "bullet"}]
                ]
            }
        }
    )
    quill.on("text-change", (delta, oldDelta, source) => {
        quillController.intervalStart()
    });
    quill.focus();
}, 10);


if( note_content ){
    setTimeout(() => {
        quill.setContents(note_content);
    }, 250);
}
