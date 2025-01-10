# Letuebici
![LE TUE BICI](https://github.com/user-attachments/assets/ce00d836-59a8-4fd5-9867-40f3e16a2482)
Description of the “Letuebici” Software
Introduction
This management software is designed to help cyclists monitor two main aspects of their hobby:
1.	Tracking Performance: Cyclists can monitor their biking performance through reports that can also be exported to Excel.
2.	Bicycle Maintenance: The software allows users to keep track of bicycle maintenance by enabling them to create maintenance items and record every replacement of a part (maintenance item).
 ![image](https://github.com/user-attachments/assets/cce1dca4-caf1-49ba-881c-0fe2fe6a463d)

It consists of six sections:
1.	CREATE BIKE
2.	UPDATE KM
3.	TRIP REPORTS
4.	VIEW STATISTICS
5.	MAINTENANCE
6.	MAINTENANCE REPORTS
Below is a brief explanation of the purpose of each section (as the program is intentionally designed to be intuitive).
Before diving into the details, I’d like to make a clarification: this is the first version of the software, the most basic one (1.0). It was initially conceived as a personal tool for use by a single individual (as implied by the name). Nevertheless, I decided to publish it on GitHub to get started (this is my very first software project).
The idea is to continue developing it by adding new features, improving the interface, and eventually making it available on smartphones. In short, I’ll strive to advance the project and evolve the software further.



Description of the Sections
1.	CREATE BIKE: This section is used to register one or more bicycle models in the database for the first time. These are the bikes that the cyclist wishes to monitor.
2.	UPDATE KM: After each bike ride, the user can log the trip by entering various details (as shown in the provided image). Recording a trip will generate a new record (a row in the table) that will be added to the trip history, viewable in the report section.
 ![image](https://github.com/user-attachments/assets/7ad65691-f006-4da6-89f9-9e2bb3b388fe)

3.	TRIP REPORTS: As shown in the image below, this section allows users to view the history report of their trips. Each row in the report represents a single bike outing. The table keeps track of the outing history and includes the following information:
•	Partial Odometer: Displays the kilometers covered during a specific trip on a given date.
•	Odometer: A cumulative total of kilometers covered across all trips, showing how many kilometers the bike has accumulated by a certain date.
•	Destination: The destination reached for each trip.
•	Data

 ![image](https://github.com/user-attachments/assets/0570dcf3-4744-4c9b-8e3e-655754b47bab)


The report can be filtered either by a specific “bike name” or by selecting all bikes. In the latter case, the report will display the complete history of all trips regardless of the bike model used.
Additionally, the report can be exported to Excel, allowing users to apply further filters. For example, users can filter by any column to obtain specific information, such as how many kilometers were covered in a year, a month, or within a particular time frame.
4.	VIEW STATISTICS: This section enables users to monitor their performance related to the trips they’ve taken, either for a specific bike or across all bikes, regardless of the model used. To begin, users must select whether to filter by a specific bike or include all bikes (by toggling the filter).
 ![image](https://github.com/user-attachments/assets/2f7ff89e-c547-4dec-89f7-7d30f7afc7f2)

Assuming a specific bike model is selected, clicking on "View Statistics" will provide the following three pieces of information:
•	Average kilometers traveled across all trips.
•	Regularity coefficient of the kilometers traveled, which measures consistency in the user's cycling habits.
•	Graph to visualize the trend of trips and compare it with the average.
 ![image](https://github.com/user-attachments/assets/706b9826-145b-4a2f-be70-7e12e55042bb)


The first piece of information is simply the average kilometers traveled across all trips, represented in the graph by a horizontal red line.
The second piece of information is a coefficient designed to represent the cyclist's regularity regarding the kilometers traveled in each trip. This is calculated using a statistical measure called the coefficient of variation, which is calculated as follows:
 ![image](https://github.com/user-attachments/assets/b620a661-7665-4c9f-8f12-20edf1cad704)

•	The closer the value is to zero, the more consistent the cyclist is.
•	The threshold value beyond which the cyclist is no longer considered regular is 0.5. A value below this threshold means the kilometers traveled on each outing are closer to each other and deviate little from the average.
The third piece of information is graphical and shows a chart of the kilometers traveled over time, comparing them with the average. The graph also allows users to view the date of a particular trip by clicking on the corresponding point in the graph.
 ![image](https://github.com/user-attachments/assets/f28bb04e-de0b-4de5-98cc-895c1619cb9b)

5.	MAINTENANCE: Each time the user performs maintenance or replaces a part on their bike, referred to as a "maintenance item" in the program, they can record the maintenance or replacement. The maintenance entry will generate a new record (a row in the report) that will be added to the maintenance history, viewable through the maintenance report (which is available in another section of the program).
When the user clicks on "Save," the software will add a new row to the history, which includes not only the data entered (bike name, maintenance item, and description) but also the date and kilometers of the bike at the time the maintenance was registered.
 ![image](https://github.com/user-attachments/assets/93953eef-60e4-4998-9675-73fb10f9edb1)

The software allows the user to create their own maintenance items, which represent the general type of the object (e.g., tires). The user can then specify additional details (e.g., model, size, etc.) in the "description" field.
The need to allow the user to create their own maintenance items and then, when recording maintenance, select one from the "maintenance item" dropdown list arises from the goal of ensuring that the system can correctly query the database. This method prevents the user from entering different strings for the same item that could be too specific or prone to typos, which could lead to errors in database searches.
For example: Without the dropdown in the "maintenance item" field, the user might enter different variations of the same item (e.g., "tire," "Tire," "tires"), leading to discrepancies when trying to search for or query that data.
 ![image](https://github.com/user-attachments/assets/b65d758b-e0c3-4db4-8be5-485ea2d87b59)

So, if we prevent the user from entering anything freely in the maintenance item field and require them to select from a dropdown list of values previously created by them, we avoid potential errors in database queries and ensure the accuracy of the information.
6.	MAINTENANCE REPORT: In this section, the user can view two reports related to maintenance. The first report shows the history of recorded maintenance, displaying the following information:
•	Bike model
•	Maintenance item
•	Description
•	Date
•	Kilometers at registration
The date and kilometers at the time of registration are automatically generated by the software when the maintenance is recorded. The current date from the computer is used for the date, and the accumulated kilometers from the bike (the last odometer value) are used for the "kilometers at registration."
In the following figure (fig. b), the "maintenance report" is shown. The user can choose whether to filter the "maintenance report" by a specific bike and maintenance item or by all bikes and/or all maintenance items.
 ![image](https://github.com/user-attachments/assets/d59a1319-3e94-4eda-bda8-1ac94a0224f6)

The second report, "Replacement Report," aims to answer questions such as:
•	"How many kilometers did my tires last?"
•	"How many kilometers did my brakes last?"
•	"Which tire model lasted the longest?"
 ![image](https://github.com/user-attachments/assets/55e48ea8-3afa-4dfd-a811-c2ff87c8d9ed)

Therefore, the "Replacement Report" will track the duration (in kilometers) for each maintenance item (calculated as the difference between the kilometers on the bike when the last maintenance of a specific item was recorded, e.g., tires, and the kilometers on the bike at the time of the new maintenance registration for the same item).
Additionally, it allows the cyclist to compare different brands and models of the same maintenance item, enabling them to determine which brand (or model) of brakes/tires/etc. lasted the longest or the shortest. This can be easily done by reviewing the duration data in the "Replacement Report."
For example, if we consider the following maintenance history (maintenance report) for the item: "tires."
 ![image](https://github.com/user-attachments/assets/d3d1a69c-1d3f-4b6e-a28b-29d8b85e526d)

The user has registered three maintenance entries so far, so the tires item has been replaced twice (because the third tire, replaced on 2025-01-18, still hasn't been replaced yet). In this case, if we view the "Replacement Report," we will see two tire replacements with their respective durations:
 ![image](https://github.com/user-attachments/assets/eaa22290-4e3f-4cd7-a523-be0557c9de4d)


The user could therefore conclude that the Pirelli model is better than the Bosch model.
P.S. The values used in these examples may not exist in a real context but are used solely for illustrative purposes.
P.S.2 Of course, it is up to the user to enter useful values in the description (at the time of the maintenance registration) in order to later compare the same replaced items but from different brands or models.
FUTURE DEVELOPMENTS:
•	Make the software usable by multiple users with account management.
•	Retrieve GPS route data from smartphones.
•	Integrate weather APIs.
•	Make the software more robust in terms of queries (with better keys).
•	Add more features to the "View Statistics" section, including statistical tests.
•	Implement machine learning algorithms to learn from maintenance data in order to improve maintenance management.
By Michele Veneziale

