# mapping
Finds the optimal meetup location for a pedestrian and driver that have differing starting locations but the same target location. By constructing a _networkx_ graph using Toronto Transit Commission (TTC) data, we call the Google Maps API only once per use. 

### Idea
Imagine Jack and Jill have plans to go to Bill's house. Jack has a vehicle and Jill does not. Jack and Jill agree that Jill will take the TTC to a place where it is convenient for Jack to pick Jill up. **What is the optimal pickup location**? Google Maps, highly accurate as it may be, does not offfer this functionality.

What if Jack is willing to go out of his way in order to save Jill time? What if we decide Jill's time is twice as valuable as Jack's time, or vice versa? What if Jill is willing to walk a certain distance? How many times is Jill wishing to get off one bus (or subway or streetcar) and get onto another? We'd like to find the optimal meetup location given these (and possibly other) parameters. 

### Tasks
 - [x] Get google maps API key
 - [x] Use API key to generate coordinates of the optimal driving path from point A to point B
 - [x] Download TTC route information
 - [x] Create graph of TTC routes
 - [x] Create TTC navigation algorithm that tells users how to get from point A to point B
 - [x] Create algorithm that finds the meetup point along Jack's path that minimizes Jill's travel time
 - [ ] Add logic that solves the problems posed in the second paragraph of the **Idea** section

### Notes
 - These algorithms will only work within range of the TTC

### Getting Started
Visit [this](https://developers.google.com/maps/documentation/embed/get-api-key) link to get your own API key. 
```
git clone https://github.com/danitamm/mapping.git
cd mapping
source setup.sh
python main.py
```
The _setup.sh_ script downloads the data, creates a virtual environment, and stores your API key. If you have issues with your API key, you can enter it manually in _keys.py_. 

The _main.py_ begins by constructing the TTC graph if it has not yet been created. It is saved to memory for future use. It then opens a command line interface that allows the user to either see a predefined example, or input a 

### Assumptions
1. People walk at a pace of 5 kilometers per hour. This pace is [widely accepted](https://www.researchgate.net/publication/5561162_Brisk_Walking_Speed_in_Older_Adults_Who_Walk_for_Exercise) to be fairly accurate.
2. The wait time for any bus, subway, or streetcar is always 7 minutes. This is slightly lower than the mean given [here](https://mobilesyrup.com/2020/01/15/moovit-2019-transit-report-canadian-cities-commute-statistics/). A lower estimate is used since most non-commuting traveling will happen downtown where buses, subways, and streetcars arrive at a higher frequency. 

### Important Caveats
1. The TTC data was gathered in November 2019. Traffic routes may have since changed. 
2. The command line interface returns not only the optimal meeting location, but also the recommended path for the TTC traveler to take (bus and subway to ride, stops at which to enter and exit, etc.). The **optimal meeting location is highly accurate, but the recommended path may be suboptimal** since it does not take real-time information into account. For best perfomance, obtain the optimal meeting location from this program, then find the optimal path to that location using Google Maps. 

### Figures
![](figures/Figure_1.png)
*A graph of all TTC routes and stops. Generated using networkx.*
