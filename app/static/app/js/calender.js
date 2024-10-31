// 
let currentYear = new Date().getFullYear();
let currentMonth = new Date().getMonth();
let events = {}; // Event dates and details

// Function to fetch events for the current month
async function fetchEvents(year, month) {
    try {
        const response = await fetch(`/get-events?year=${year}&month=${month + 1}`);
        const data = await response.json();
        events = data; // JSON形式のデータを events に格納
        createCalendar(year, month); // 新しいイベントデータでカレンダーを再描画
    } catch (error) {
        console.error("Error fetching events:", error);
    }
}

// Update createCalendar function to show fetched events
function createCalendar(year, month) {
    const monthDays = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
    const daysInMonth = new Date(year, month + 1, 0).getDate();
    const firstDay = new Date(year, month, 1).getDay();

    let calendarHTML = '<table class="calendar"><thead><tr>';
    for (let day of monthDays) calendarHTML += `<th>${day}</th>`;
    calendarHTML += '</tr></thead><tbody>';

    let dayCount = 1;
    let prevMonthDayCount = new Date(year, month, 0).getDate() - firstDay + 1;

    for (let i = 0; i < 6; i++) {
        calendarHTML += '<tr>';
        for (let j = 0; j < 7; j++) {
            let date = `${year}-${String(month + 1).padStart(2, '0')}-${String(dayCount).padStart(2, '0')}`;
            if (i === 0 && j < firstDay) {
                calendarHTML += `<td class="mute">${prevMonthDayCount++}</td>`;
            } else if (dayCount > daysInMonth) {
                calendarHTML += `<td class="mute">${dayCount++ - daysInMonth}</td>`;
            } else {
                let eventText = events[date] ? `<br><span class="event">${events[date]}</span>` : '';
                calendarHTML += `<td onclick="openModal('${date}')">${dayCount++}${eventText}</td>`;
            }
        }
        calendarHTML += '</tr>';
        if (dayCount > daysInMonth) break;
    }

    calendarHTML += '</tbody></table>';
    document.getElementById('calendar').innerHTML = calendarHTML;
    document.getElementById('monthDisplay').textContent = `${new Date(year, month).toLocaleString('default', { month: 'long' })} ${year}`;
}

// Adjust changeMonth function to fetch events for the new month
function changeMonth(delta) {
    currentMonth += delta;
    if (currentMonth < 0) {
        currentYear--;
        currentMonth = 11;
    } else if (currentMonth > 11) {
        currentYear++;
        currentMonth = 0;
    }
    fetchEvents(currentYear, currentMonth);
}

window.onload = function() {
    fetchEvents(currentYear, currentMonth); // Fetch events on initial load
};
