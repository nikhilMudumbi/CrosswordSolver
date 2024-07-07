document.getElementById('uploadForm').addEventListener('submit', function(event) {
    event.preventDefault(); // Prevent the default form submission behavior
    const fileInput = document.getElementById('fileInput');
    const file = fileInput.files[0]; // Get the file from the input
    const formData = new FormData(); // Create a FormData object
    formData.append('file', file); // Append the file to the FormData object
    console.log(file)

    fetch('/upload', {
        method: 'POST', // Send a POST request to the '/upload' endpoint
        body: formData // Include the FormData object in the request body
    }).then(response => response.json()) // Convert the response to JSON
      .then(data => {
          if (data.error) {
              console.error('Error:', data.error);
          } else {
              displayGrid(data.grid); // Call displayGrid with the received grid data

              document.getElementById('solveButton').style.display = 'block';
          }
      }).catch(error => {
          console.error('Error:', error); // Log any errors to the console
      });
});

document.getElementById('solveButton').addEventListener('click', function() {
    fetch('/solve', {
        method: 'POST' // Send a POST request to the '/solve' endpoint
    }).then(response => response.json()) // Convert the response to JSON
      .then(data => {
          console.log(typeof data.grid);
          for (let i = 0; i < 15; i++) {
            for (let j = 0; j < 15; j++) {
                console.log(data.grid[i][j]);
            }
          }
          addLetters(data.grid); // Call displayGrid with the received solved grid data
      }).catch(error => {
          console.error('Error:', error); // Log any errors to the console
      });
});

/*function displayGrid(grid) {
    const gridContainer = document.getElementById('gridContainer');
    gridContainer.innerHTML = ''; // Clear the current grid
    grid.forEach(row => {
        row.forEach(cell => {
            const div = document.createElement('div');
            div.className = `cell ${cell === -1 ? 'black' : 'white'}`; // Set the class based on the cell value ('black' or 'white')
            gridContainer.appendChild(div); // Append the cell to the grid container
        });
    });
}*/

function displayGrid(grid) {
    const gridContainer = document.getElementById('gridContainer');
    gridContainer.innerHTML = ''; // Clear the current grid

    grid.forEach(row => {
        row.forEach(cell => {
            const div = document.createElement('div');
            // Assign class based on the cell value ('black' or 'white')
            div.className = `cell ${cell === -1 ? 'black' : 'white'}`;
            // Add number label if cell number is not -1
            if (cell > 0) {
                const numberLabel = document.createElement('span');
                numberLabel.className = 'number-label';
                numberLabel.textContent = cell;
                div.appendChild(numberLabel);
            }
            if (cell > -1) {
                // Add input box inside the cell
                const inputBox = document.createElement('input');
                inputBox.type = 'text';
                inputBox.className = 'letter-input';
                inputBox.maxLength = 1; // Only allow one letter
                div.appendChild(inputBox);
            }
            gridContainer.appendChild(div); // Append the cell to the grid container
        });
    });
}

function addLetters(lettersGrid) {
    console.log("here");
    console.log(lettersGrid);
    console.log(typeof lettersGrid);
    console.log(lettersGrid[0]);
    console.log(lettersGrid[0][0]);
    const gridContainer = document.getElementById('gridContainer');
    const inputElements = gridContainer.querySelectorAll('.letter-input');
    const cellElements = gridContainer.querySelectorAll('.cell');

    // Loop through each input element and assign corresponding letter from lettersGrid

    cellElements.forEach((cell, index) => {
        let row = Math.floor(index / 15);
        let col = index % 15;
        console.log(row);
        console.log(col);
        console.log(lettersGrid[row][col]);
        const letter = lettersGrid[row][col];
        if (letter !== ' ') {
            const textBox = cell.querySelector('.letter-input');
            textBox.value = letter;
        }
    });
    /* inputElements.forEach((input, index) => {
        const row = Math.floor(index / 15);  // Calculate row index
        const col = index % 15;              // Calculate column index
        const letter = lettersGrid[row][col]; // Get letter from lettersGrid
        console.log(lettersGrid[row][col]);
        
        input.value = letter; // Assign letter to input value
    }); */
} 