document.addEventListener('DOMContentLoaded', function() {
    const stats = [
        { id: 'years-experience', target: 6, duration: 2000 },
        { id: 'properties-sold', target: 11, duration: 2000 },
        { id: 'ongoing-projects', target: 23, duration: 2000 },
        { id: 'completed-projects', target: 7, duration: 2000 }
    ];

    stats.forEach(stat => {
        const element = document.getElementById(stat.id);
        let count = 0;
        const increment = Math.ceil(stat.target / (stat.duration / 100));
        
        // Update the stat with the "+" sign      
        const interval = setInterval(() => {
            count += increment;
            if (count >= stat.target) {
                count = stat.target; // Ensure it doesn't go over
                clearInterval(interval);
            }
            element.textContent = count + '+'; // Ensure the "+" is appended correctly
        }, 100);
    });
});
