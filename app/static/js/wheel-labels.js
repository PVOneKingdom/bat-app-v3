function handleMouseOverBody(show, element) {
    if (typeof window.isMouseOverBodyLoaded === "boolean" && window.isMouseOverBodyLoaded) return; // Prevent re-initialization
    window.isMouseOverBodyLoaded = true; // Mark as loaded

    if (!show || !element) return;

    let labelDiv = null;

    document.body.addEventListener("mouseover", (e) => {
        // Check if the target is a "path" and the parent element contains the "category" class
        if (e.target.tagName.toLowerCase() === "path" && e.target.parentElement.classList.contains("category")) {
            // Create a div label if it doesn't exist
            if (!labelDiv) {
                labelDiv = document.createElement("div");
                labelDiv.style.position = "absolute";
                labelDiv.style.backgroundColor = "#EEEFF2";
                labelDiv.style.color = "#000";
                labelDiv.style.padding = "8px 15px";
                labelDiv.style.borderRadius = "4px";
                labelDiv.style.pointerEvents = "none"; // Prevent interactions with the label
                labelDiv.style.zIndex = "1000";
                document.body.appendChild(labelDiv);
            }

            // Set the content of the label
            labelDiv.textContent = e.target.parentElement.getAttribute("data-category_name") || "";

            // Update the position of the label as the mouse moves
            const mouseMoveHandler = (moveEvent) => {
                if (labelDiv) { // Ensure labelDiv exists
                    labelDiv.style.left = `${moveEvent.pageX + 10}px`;
                    labelDiv.style.top = `${moveEvent.pageY + 10}px`;
                }
            };

            document.addEventListener("mousemove", mouseMoveHandler);

            // Remove the label and cleanup when the mouse leaves the target element
            const mouseLeaveHandler = () => {
                if (labelDiv) {
                    labelDiv.remove();
                    labelDiv = null;
                }
                document.removeEventListener("mousemove", mouseMoveHandler);
                e.target.removeEventListener("mouseleave", mouseLeaveHandler);
            };

            e.target.addEventListener("mouseleave", mouseLeaveHandler);
        }
    });

    document.body.addEventListener("mousemove", (e) => {
        // Prevent errors by ensuring labelDiv is only manipulated when it exists
        if (!labelDiv) return;
    });
}

// Initialize the label behavior after a 200ms delay
setTimeout(() => {
    handleMouseOverBody(true, document.body);
}, 200);

