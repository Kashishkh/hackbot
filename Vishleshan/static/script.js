document.addEventListener('DOMContentLoaded', function () {
    const welcomeText = document.getElementById('welcome-text');
    const appText = document.getElementById('app-text');

    welcomeText.innerHTML = ''; // Clear the initial text
    appText.innerHTML = ''; // Clear the initial text

    const welcomeString = 'Welcome To ';
    const appString = 'Vishleshan App';

    function typeText(element, text) {
        let i = 0;
        const intervalId = setInterval(function () {
            if (i < text.length) {
                element.innerHTML += text.charAt(i);
                i++;
            } else {
                clearInterval(intervalId);
            }
        }, 100);
    }

    typeText(welcomeText, welcomeString);
    setTimeout(function () {
        typeText(appText, appString);
    }, welcomeString.length * 100); // Delay the second text to start after the first one finishes typing

    const categoryDropdown = document.getElementById('category');
    const itemDropdown = document.getElementById('item');

    categoryDropdown.addEventListener('change', function () {
        const selectedCategory = this.value;
        updateItemDropdown(selectedCategory);
    });

    function updateItemDropdown(selectedCategory) {
        $.ajax({
            type: 'POST',
            url: '/get_items',
            data: { 'category': selectedCategory },
            success: function (data) {
                itemDropdown.innerHTML = "<option value='' disabled selected>Select Item</option>";
                data.items.forEach(item => {
                    const option = document.createElement('option');
                    option.value = item;
                    option.text = item;
                    itemDropdown.add(option);
                });
            }
        });
    }
});
