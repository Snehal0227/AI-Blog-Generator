// Monthly Views Chart

const views = document.getElementById("viewsChart");

if (views) {

    new Chart(views, {

        type: "line",

        data: {

            labels: ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],

            datasets: [{

                label: "Views",

                data: [1200, 2500, 3100, 4200, 5100, 6400],

                borderColor: "#7C3AED",

                backgroundColor: "rgba(124,58,237,.15)",

                fill: true,

                tension: .4

            }]

        },

        options: {

            responsive: true,

            plugins: {

                legend: {

                    display: true

                }

            }

        }

    });

}



// Traffic Chart

const traffic = document.getElementById("trafficChart");

if (traffic) {

    new Chart(traffic, {

        type: "doughnut",

        data: {

            labels: ["Google", "Facebook", "Instagram", "Direct"],

            datasets: [{

                data: [45, 20, 18, 17],

                backgroundColor: [

                    "#7C3AED",

                    "#3B82F6",

                    "#EC4899",

                    "#10B981"

                ]

            }]

        },

        options: {

            responsive: true

        }

    });

}