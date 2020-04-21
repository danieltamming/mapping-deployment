# mapping-deployment
Finds the optimal meetup location for a pedestrian and driver that have differing starting locations but the same target location. By constructing a _networkx_ graph using Toronto Transit Commission (TTC) data, we call the Google Directions and Geolocation APIs only once each per use. 

### Idea
Imagine Jack and Jill have plans to go to Bill's house. Jack has a vehicle and Jill does not. Jack and Jill agree that Jill will take the TTC to a place where it is convenient for Jack to pick Jill up. **What is the optimal pickup location**? Google Maps, highly accurate as it may be, does not offfer this functionality.

What if Jack is willing to go out of his way in order to save Jill time? What if we decide Jill's time is twice as valuable as Jack's time, or vice versa? What if Jill is willing to walk a certain distance? How many times is Jill wishing to get off one bus (or subway or streetcar) and get onto another? We'd like to find the optimal meetup location given these (and possibly other) parameters. 

### Messenger Bot Use (pending approval from Facebook)
Users are asked to send the bot the pedestrian's location, the driver's location, and their shared final destination, separated by periods.

### Tasks
 - [x] Get google maps API key
 - [x] Use API key to generate coordinates of the optimal driving path from point A to point B
 - [x] Download TTC route information
 - [x] Create graph of TTC routes
 - [x] Create TTC navigation algorithm that tells users how to get from point A to point B
 - [x] Create algorithm that finds the meetup point along Jack's path that minimizes Jill's travel time
 - [x] Deploy program as Facebook Messenger chatbot
 - [ ] Receive app approval from Facebook
 - [ ] Add logic that solves the problems posed in the second paragraph of the **Idea** section

### Notes
 - Pedestrian must be in range of the TTC

### Assumptions
1. People walk at a pace of 5 kilometers per hour. This pace is [widely accepted](https://www.researchgate.net/publication/5561162_Brisk_Walking_Speed_in_Older_Adults_Who_Walk_for_Exercise) to be fairly accurate.
2. The wait time for any bus, subway, or streetcar is always 7 minutes. This is slightly lower than the mean given [here](https://mobilesyrup.com/2020/01/15/moovit-2019-transit-report-canadian-cities-commute-statistics/). A lower estimate is used since most non-commuting traveling will happen downtown where buses, subways, and streetcars arrive at a higher frequency. 

### Important Caveats
 - The TTC data was gathered in November 2019. Traffic routes may have since changed. 

### Figures
![](figures/Figure_1.png)
*A graph of all TTC routes and stops. Generated using networkx.*
