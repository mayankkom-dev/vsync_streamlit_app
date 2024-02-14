<script>
            function flipCard(card) {
                card.classList.toggle('is-flipped');
            }

            function openLink(event) {
                // Prevent the card from flipping when clicking on the link
                event.stopPropagation();
            }
            //function openPopup(url) {
            // Show the popup
            //document.getElementById('popup').style.display = 'block';

            // Load the content into the iframe
            //document.getElementById('popupFrame').src = url;
            //}

            //function closePopup() {
            // Hide the popup
            //document.getElementById('popup').style.display = 'none';

            // Clear the iframe content
            //document.getElementById('popupFrame').src = 'about:blank';
            //}
</script> 