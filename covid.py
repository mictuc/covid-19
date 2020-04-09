# Covid Plotter
# Michael Tucker

## TODO:
# add selection for counties/states
# make buttons to switch b/w bay and regions (only display 3 at a time)
# make reset button
# make button for log vs. normal exponential on time cases

import matplotlib
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, RadioButtons
import datetime
import pandas as pd
pd.options.mode.chained_assignment = None

BAY_AREA = [('Santa Clara','California'),('San Mateo', 'California'),('San Francisco','California'),('Alameda','California'),('Santa Cruz','California'),('Contra Costa','California'),('Marin','California')]
DATA_FILE = 'covid-19-data/us-counties.csv'
OTHER_AREAS = [('Los Angeles','California'),('California'),('New York City','New York'),('New York'),('Rhode Island'),('Washington')]

rolling_window = 7
today = datetime.date.today()
viewing_date = today

df=pd.read_csv('covid-19-data/us-counties.csv', sep=',',parse_dates=['date'], header=0)

fig, axes = plt.subplots(nrows=2, ncols=3, figsize=(20,10))
axcolor = 'lightgoldenrodyellow'
axwindow = plt.axes([0.35, 0.05, 0.3, 0.03], facecolor=axcolor)
axdate = plt.axes([0.35, 0.01, 0.3, 0.03], facecolor=axcolor)

swindow = Slider(axwindow, 'Rolling Window', 1, 14, valinit=7, valstep=1, valfmt='%d')
dt = (today-datetime.date(2020,3,1)).days
sdate = Slider(axdate, 'Date', matplotlib.dates.date2num(datetime.date(2020,3,1)), matplotlib.dates.date2num(viewing_date), valinit=matplotlib.dates.date2num(viewing_date),valstep=1)
sdate.valtext.set_text(viewing_date.strftime("%Y-%m-%d"))

def plot(region_data, name, ax):
    region_data_temp = region_data.loc[(region_data['date'] <= pd.Timestamp(viewing_date))]
    region_data_temp.plot(kind='line',x='date',y='cases',label=name, ax=axes[ax,0])
    region_data_temp.plot(kind='line',x='cases',y=('avg new '+str(rolling_window)),loglog=True,label=name,ax=axes[ax,1])
    region_data_temp.plot(kind='line',x='cases',y=('growth '+str(rolling_window)),label=name, ax=axes[ax,2])

def analyze_data(region_data):
    region_data['new cases'] = region_data['cases'].shift(-1) - region_data['cases']
    for i in range(1,15):
        region_data['avg new '+str(i)] = region_data['new cases'].rolling(i).sum()
        region_data['growth '+str(i)] = region_data['avg new '+str(i)] / region_data['cases']

def generate_plots():
    plot(bay_data, 'Bay Area',0)
    plot(bay_data, 'Bay Area',1)
    for place in bay_county_data.keys():
        county, state = place
        plot(bay_county_data[place], county,0)

    for place in other_area_data.keys():
        if len(place) == 2:
            county, state = place
            plot(other_area_data[place], county, 1)
        else:
            state = place
            plot(other_area_data[place], state, 1)

def clear_plots():
    for i in range(2):
        for j in range(3):
            axes[i,j].cla()

def update(val):
    global rolling_window
    rolling_window = int(swindow.val)
    global viewing_date
    viewing_date = matplotlib.dates.num2date(sdate.val).date()
    sdate.valtext.set_text(viewing_date.strftime("%Y-%m-%d"))
    clear_plots()
    generate_plots()
    format_plots()
    fig.canvas.draw_idle()

def analyze_places(places):
    place_data = {}
    for place in places:
        if len(place) == 2:
            county, state = place
            county_data = df.loc[(df['county'] == county) & (df['state'] == state)]
            analyze_data(county_data)
            place_data[place] = county_data
        else:
            state = place
            state_data = df.loc[df['state'] == state].groupby(['date']).sum().reset_index()
            analyze_data(state_data)
            place_data[place] = state_data
    return place_data

def analyze_bay_area():
    bay_data = df[df[['county','state']].apply(tuple, 1).isin(BAY_AREA)].groupby(['date']).sum().reset_index()
    analyze_data(bay_data)
    county_data = analyze_places(BAY_AREA)
    return (bay_data, county_data)

def format_plots():
    fig.subplots_adjust(left=0.04, bottom=0.15, right=0.98, top=0.96, wspace=0.20, hspace=0.32)

    axes[0,0].set_title('Bay Area Cases By Date')
    axes[0,0].set_xlabel('Date')
    axes[0,0].set_ylabel('Cases')
    axes[0,0].set_xlim(left=datetime.date(2020, 3, 1))
    axes[0,0].legend(ncol=2, shadow=True, fontsize='small',fancybox=True)
    axes[0,0].set_yscale('log')

    axes[0,1].set_title('Bay Area New Cases vs. Total Cases')
    axes[0,1].set_xlabel('Total Cases')
    axes[0,1].set_ylabel('New Cases in Past ' + str(rolling_window) + ' days')
    axes[0,1].set_xlim(left=50)
    axes[0,1].legend(ncol=2, shadow=True, fontsize='small',fancybox=True)

    axes[0,2].set_title('Bay Area New Case Growth vs. Total Cases')
    axes[0,2].set_xlabel('Total Cases')
    axes[0,2].set_ylabel('Growth of New Cases in Past ' + str(rolling_window) + ' days')
    axes[0,2].set_xlim(left=50)
    axes[0,2].set_ylim(top=2)
    axes[0,2].set_xscale('log')
    axes[0,2].legend(ncol=2, shadow=True, fontsize='small',fancybox=True)

    axes[1,0].set_title('Cases By Date')
    axes[1,0].set_xlabel('Date')
    axes[1,0].set_ylabel('Cases')
    axes[1,0].set_xlim(left=datetime.date(2020, 3, 1))
    axes[1,0].set_yscale('log')
    axes[1,0].legend(ncol=2, shadow=True, fontsize='small',fancybox=True)

    axes[1,1].set_title('New Cases vs. Total Cases')
    axes[1,1].set_xlabel('Total Cases')
    axes[1,1].set_ylabel('New Cases in Past ' + str(rolling_window) + ' days')
    axes[1,1].set_xlim(left=50)
    axes[1,1].legend(ncol=2, shadow=True, fontsize='small',fancybox=True)

    axes[1,2].set_title('New Case Growth vs. Total Cases')
    axes[1,2].set_xlabel('Total Cases')
    axes[1,2].set_ylabel('Growth of New Cases in Past ' + str(rolling_window) + ' days')
    axes[1,2].set_xlim(left=50)
    axes[1,2].set_ylim(top=2)
    axes[1,2].set_xscale('log')
    axes[1,2].legend(loc="lower left",ncol=2, shadow=True, fontsize='small',fancybox=True)


(bay_data, bay_county_data) = analyze_bay_area()
other_area_data = analyze_places(OTHER_AREAS)
generate_plots()
format_plots()

swindow.on_changed(update)
sdate.on_changed(update)

plt.show()
