
function getMatchId()
{
    const getArgs = window.location.hash.split("?")[1]
    args = m.parseQueryString(getArgs)
    return args.matchId
}

function apiRequest(matchId)
{
    return m.request({
        method: "get",
        url: "/api/stats/",
        async: "false",
        params: {matchId: matchId},
    })
    .then(function(response) {
        if (response.err == true)
        {
            displayError(err.message, "error-wrap");
            return ;
        }
                const matchInfos = JSON.parse(response.matchData);
                const goalsPlayer1 = JSON.parse(response.goalsPlayer1);
                const goalsPlayer2 = JSON.parse(response.goalsPlayer2);
                return {
                    matchInfos,
                    goalsPlayer1,
                    goalsPlayer2
                };
    })
    .catch(function(err){
        console.log('request failed: ' + err)
        return null
    })
}

function parseTime(timeStr)
{
    const [hours, minutes, seconds] = timeStr.split(':').map(Number);
    const totalSeconds = minutes * 60 + seconds;
    const returnSeconds = Math.min(totalSeconds, 119); // Make sure the sudden death goals after 2 mins are in 2 mins.
    return Math.floor(returnSeconds / 30);
}

function parseGoals(matchData)
{
    const intervalSeconds = 30;
    const totalDuration = 120;
    const numBuckets = totalDuration / intervalSeconds;

    const statsPlayer1 = Array(numBuckets + 1).fill(0);
    const statsPlayer2 = Array(numBuckets + 1).fill(0);

    for (let i = 0; i < matchData.goalsPlayer1.length; i++) {
        const bucket = parseTime(matchData.goalsPlayer1[i]);
        if (bucket < numBuckets)
            statsPlayer1[bucket + 1]++;
    }

    for (let i = 0; i < matchData.goalsPlayer2.length; i++) {
        const bucket = parseTime(matchData.goalsPlayer2[i]);
        if (bucket < numBuckets)
            statsPlayer2[bucket + 1]++;
    }

    for (let i = 1; i <= numBuckets; i++) {
        statsPlayer1[i] += statsPlayer1[i - 1];
        statsPlayer2[i] += statsPlayer2[i - 1];
    }

    return { statsPlayer1, statsPlayer2 };
}

async function loadCharts(matchId)
{
    if (!document.getElementById("ChartsLoaded")) /* If chart div is not loaded */
        return;
    matchData = await apiRequest(matchId);
    if (!matchData)
        return;
    matchData = await Object.assign(parseGoals(matchData), matchData);
    loadLineChart(matchData);
    loadDoughnutChart(matchData);
}

function loadDoughnutChart(matchData)
{
    const totalIntervals = matchData.statsPlayer1.length - 1;

    doughnut = document.getElementById('doughnutChart');
    new Chart(doughnut, {
        type: 'doughnut',
        data: {
            labels: [
                matchData.matchInfos.usernamePlayer1 + ' avg goals per 30s',
                matchData.matchInfos.usernamePlayer2 + ' avg goals per 30s',
            ],
            datasets: [{
                label: 'Average goals per minute',
                data: [
                    matchData.statsPlayer1[totalIntervals] / totalIntervals,
                    matchData.statsPlayer2[totalIntervals] / totalIntervals, ],
                backgroundColor: [
                    '#244aa5', // Kosovo Blue
                    '#D0A650', // Kosovo Yellow
                  ],
                borderColor: [
                    '#244aa5', // Kosovo Blue
                    '#D0A650', // Kosovo Yellow
                ],
                hoverOffset: 4,
            }],
            options: {
                responsive: true, // ??? do we ?
                maintainratio: false,
                plugin: {
                    legend: {
                        position: 'top'
                    }
                }
            }
        },
    });
}


function loadLineChart(matchData)
{
    line = document.getElementById('lineChart');
    new Chart(line, {
        type: 'line',
        data: {
        labels: ['0:00', '0:30', '1:00', '1:30', '2:00'],
        datasets: [{
            label: matchData.matchInfos.usernamePlayer1 + ' goals',
            data: matchData.statsPlayer1,
            borderColor: ['#244aa5'], // Kosovo Blue
            backgroundColor: ['#244aa5'], // Kosovo Blue
        },
        {
            label: matchData.matchInfos.usernamePlayer2 + ' goals',
            data: matchData.statsPlayer2,
            borderColor: ['#D0A650'], // Kosovo Yellow
            backgroundColor: ['#D0A650'], // Kosovo Yellow
        }]
        },
        options: {
            responsive: true, // ??? do we ?
            maintainratio: false,
            scales: {
            y: {
                title: {
                    display: true,
                    text: 'Score',

                },
                beginAtZero: true
            },
            x: {
                title: {
                    display: true,
                    text: 'Time (mins)',

                }
            }
            },
            label: 'Evolution of goals during the match',
            title: {
                display: true,
                text: 'Evolution of goals during the match',
            }
        }
    });
}

