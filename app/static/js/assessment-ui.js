
class AssessmentUI {

    constructor() {
        self.answerRadios = document.querySelectorAll("#answer-value-wrapper input");
        self.answerDescription = document.querySelectorAll("#answer-description-textarea");
    }
    
    clearAnswers(){
        answerRadios.forEach(element => {
            element.checked = false;
        });
    }
}



if( typeof(assessmentUI) === "undefined" ){
    var assessmentUI = new AssessmentUI()
}
