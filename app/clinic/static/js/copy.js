document.addEventListener('DOMContentLoaded', function() {
    var cells = document.querySelectorAll('td#copy__data');
    
    cells.forEach(function(cell) {
        cell.addEventListener('click', function() {
            var text = this.innerText;
            
            navigator.clipboard.writeText(text)
                .then(function() {
                    var message = document.createElement('div');
                    message.innerHTML = 'Copying successful!';
                    message.style.position = 'fixed';
                    message.style.top = '10px';
                    message.style.left = '10px';
                    message.style.padding = '10px';
                    message.style.background = 'green';
                    message.style.color = 'white';
                    
                    document.body.appendChild(message);
                    
                    setTimeout(function() {
                        message.remove();
                    }, 2000);
                })
                .catch(function(error) {
                    console.error('Copying failed:', error);
                });
        });
    });
});