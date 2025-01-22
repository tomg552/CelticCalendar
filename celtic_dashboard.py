import streamlit as st
import datetime
import ephem
import matplotlib.pyplot as plt
from skyfield.api import load
from skyfield.almanac import find_discrete, seasons

# Inject custom font via HTML
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=IM+Fell+English&display=swap');
    html, body, [class*="css"] {
        font-family: 'IM Fell English', serif;
    }
    </style>
""", unsafe_allow_html=True)

# Define Celtic calendar constants
MONTH_NAMES = [
    "Samonios", "Dumannios", "Riuros", "Anagantios", "Ogronios",
    "Cutios", "Giamonios", "Simivisonios", "Equos", "Elembivos",
    "Aedrinios", "Cantlos", "Sonnocingos"
]
MONTH_LENGTHS = [30, 29]  # Alternating lengths for regular months
INTERCALARY_LENGTH = 30  # Length of the intercalary month
CYCLE_YEARS = 5  # 5-year cycle duration

# Utility Functions
def calculate_luck_phase(celtic_day, lunar_phase):
    if lunar_phase == "Full Moon":
        return "Very Lucky"
    elif lunar_phase == "New Moon":
        return "Lucky" if celtic_day % 2 == 1 else "Neutral"
    elif "Waxing" in lunar_phase:
        return "Lucky"
    elif "Waning" in lunar_phase:
        return "Neutral" if celtic_day % 2 == 0 else "Unlucky"
    else:
        return "Unlucky"

def find_first_new_moon(year):
    jan_1 = ephem.Date(datetime.date(year, 1, 1))
    moon = ephem.Moon()
    while True:
        moon.compute(jan_1)
        if moon.phase < 1:
            return jan_1.datetime().date()
        jan_1 = ephem.Date(jan_1 + 1)

def build_celtic_year(year):
    cycle_year = (year - 2025) % CYCLE_YEARS + 1
    months = [MONTH_LENGTHS[i % 2] for i in range(12)]
    if cycle_year in [3, 5]:
        months.append(INTERCALARY_LENGTH)
    return months

def calculate_celtic_date(gregorian_date):
    celtic_year_start = find_first_new_moon(gregorian_date.year)
    if gregorian_date < celtic_year_start:
        celtic_year_start = find_first_new_moon(gregorian_date.year - 1)
    delta_days = (gregorian_date - celtic_year_start).days
    celtic_month_lengths = build_celtic_year(celtic_year_start.year)
    for month_index, days_in_month in enumerate(celtic_month_lengths):
        if delta_days < days_in_month:
            return MONTH_NAMES[month_index], delta_days + 1
        delta_days -= days_in_month
    return MONTH_NAMES[0], 1

def calculate_lunar_phase(gregorian_date):
    moon = ephem.Moon()
    moon.compute(ephem.Date(gregorian_date))
    phase = moon.phase
    if phase < 25:
        return "New Moon"
    elif phase < 50:
        return "Waxing Crescent"
    elif phase < 75:
        return "Full Moon"
    else:
        return "Waning Crescent"

def lunar_phase_ascii(phase):
    """Generate an ASCII art representation of the moon phase."""
    if phase < 1:  # New Moon
        return "🌑 New Moon"
    elif phase < 25:  # Waxing Crescent
        return "🌒 Waxing Crescent"
    elif phase < 50:  # First Quarter
        return "🌓 First Quarter"
    elif phase < 75:  # Waxing Gibbous
        return "🌔 Waxing Gibbous"
    elif phase < 100:  # Full Moon
        return "🌕 Full Moon"
    elif phase < 125:  # Waning Gibbous
        return "🌖 Waning Gibbous"
    elif phase < 150:  # Last Quarter
        return "🌗 Last Quarter"
    else:  # Waning Crescent
        return "🌘 Waning Crescent"

def get_solstices_and_equinoxes(year):
    # Load ephemeris data
    eph = load('de421.bsp')  # Use an accurate dataset like 'de430.bsp'
    timescale = load.timescale()

    # Define the time range for the year
    start_time = timescale.utc(year, 1, 1)
    end_time = timescale.utc(year + 1, 1, 1)

    # Calculate solstices and equinoxes
    times, events = find_discrete(start_time, end_time, seasons(eph))
    event_names = ['Spring Equinox', 'Summer Solstice', 'Fall Equinox', 'Winter Solstice']
    return {event_names[event]: time.utc_iso() for time, event in zip(times, events)}
    celestial_events = get_solstices_and_equinoxes(year)
    print(celestial_events)

# Sidebar Content
st.sidebar.title("Celtic Calendar Settings")

# Sidebar: Select a Base Date
selected_date = st.sidebar.date_input("Select a Date", datetime.date.today())

# Sidebar: Adjust Date Relative to Selected Date
date_offset = st.sidebar.number_input(
    "Days from Selected Date:",
    value=0,  # Default to no offset
    step=1,  # Adjust by days
    format="%i"
)

year = navigated_date.year
celestial_events = get_solstices_and_equinoxes(year)

# Sidebar: Display dynamic celestial events

arawn_lore = [
    "Arawn is the king of Annwn, the Otherworld in Welsh mythology.",
    "Arawn is associated with death, healing, and the balance between worlds.",
    "The hounds of Arawn are white with red ears, often seen as guides or omens.",
    "Annwn, ruled by Arawn, is a realm of peace, abundance, and mystery.",
    "Arawn's rivalry with Hafgan shows the eternal battle between forces of nature."
]
daily_lore = arawn_lore[navigated_date.day % len(arawn_lore)]
st.sidebar.header("Celtic Mythology Insight")
st.sidebar.markdown(f"**{daily_lore}**")

moon_phase_lore = {
    "New Moon": "A time of beginnings, reflection, and connecting with Annwn.",
    "Full Moon": "Symbolic of completion, clarity, and the height of power.",
    "Waxing Crescent": "A time for growth and setting intentions.",
    "Waning Crescent": "A time for release and preparing for renewal.",
    "Waxing Gibbous": "Momentum builds toward fulfilment.",
    "Waning Gibbous": "A time to express gratitude and share wisdom.",
}
st.sidebar.markdown("### 🌕 **Moon Lore**")
st.sidebar.markdown(f"**{moon_phase_lore.get(lunar_phase, 'Mysteries of the moon abound.')}**")

ritual_suggestions = {
    "New Moon": ["Light a black or white candle to honour Arawn's connection to transformation."],
    "Full Moon": ["Set intentions for clarity and insight.", "Offer seasonal fruits or nuts."]
}
st.sidebar.subheader("Ritual Suggestions")
for suggestion in ritual_suggestions.get(lunar_phase, ["Reflect on Arawn's mysteries."]):
    st.sidebar.markdown(f"- {suggestion}")

# Main Page Content
col1, col2 = st.columns(2)

with col1:
    st.title("Celtic Calendar")
    st.markdown(f"## 🕊️ **Celtic Calendar Date:** {celtic_month} {celtic_day}")
    st.markdown(f"#### (Gregorian Date: {navigated_date})")
    festival_today = "No festival today."

    festivals = {
        "Elembivos 19": "Samhain (Festival of the Dead, Arawn's peak influence).",
        "Samonios 12": "Imbolc (Festival of Lights)",
        "Anagantios 12": "Beltane (Festival of Fire)",
        "Giamonios 16": "Lughnasadh (Harvest Festival)",
        "Cantlos 10": "Winter Solstice (Arawn's realm is at its most mysterious).",
        "Dumannios 29": "Spring Equinox (Balance between light and dark).",
        "Cutios 3": "Summer Solstice (Celebration of abundance).",
        "Equos 9": "Autumn Equinox (Transition into reflection).",
    }

    festival_dates = []
    for key, name in festivals.items():
        month, day = key.split()
        month_index = MONTH_NAMES.index(month)
        celtic_days_from_start = sum(build_celtic_year(navigated_date.year)[:month_index]) + int(day)
        gregorian_festival_date = find_first_new_moon(navigated_date.year) + datetime.timedelta(days=celtic_days_from_start)
        festival_dates.append((gregorian_festival_date, name))

    for date, name in festival_dates:
        if date == navigated_date:
            festival_today = name
            break

    st.markdown(f"**Festival Today:** {festival_today}")

    next_festivals = [f for f in festival_dates if f[0] > navigated_date]
    if next_festivals:
        next_festival_date, next_festival_name = min(next_festivals, key=lambda x: x[0])
        days_to_next_festival = (next_festival_date - navigated_date).days
        if days_to_next_festival < 30:
            st.markdown(f"**Next Festival:** {next_festival_name} in {days_to_next_festival} days!")

    st.markdown("**Celestial Events**")
    try:
        celestial_events = get_solstices_and_equinoxes(year)
        for event, date in celestial_events.items():
            days_away = (datetime.date.fromisoformat(date[:10]) - navigated_date).days
            if days_away >= 0:
                st.markdown(f"- **{event}:** {date[:10]} ({days_away} days away)")
    except Exception as e:
        st.markdown.error(f"Error calculating celestial events: {e}")

with col2:
    st.title("Lunar Phases")
    st.markdown(f"**Lunar Phase:** {lunar_phase}")

    moon = ephem.Moon()
    moon.compute(ephem.Date(navigated_date))
    ascii_art = lunar_phase_ascii(moon.phase)
    st.markdown(f"### **Moon Phase for {celtic_month} {celtic_day}:** {ascii_art}")

    st.markdown("#### Moon Phases for the Next 3 Days:")
    next_phases = []
    for i in range(1, 4):
        next_date = navigated_date + datetime.timedelta(days=i)
        moon.compute(ephem.Date(next_date))
        next_phases.append((next_date, lunar_phase_ascii(moon.phase)))

    for next_date, phase in next_phases:
        st.markdown(f"- **{next_date}:** {phase}")

    today_lunar_phase = calculate_lunar_phase(navigated_date)
    today_luck = calculate_luck_phase(celtic_day, today_lunar_phase)

    tomorrow_date = navigated_date + datetime.timedelta(days=1)
    tomorrow_celtic_month, tomorrow_celtic_day = calculate_celtic_date(tomorrow_date)
    tomorrow_lunar_phase = calculate_lunar_phase(tomorrow_date)
    tomorrow_luck = calculate_luck_phase(tomorrow_celtic_day, tomorrow_lunar_phase)

    def luck_to_bar(luck):
        luck_mapping = {
            "Very Lucky": (100, "green"),
            "Lucky": (70, "lightgreen"),
            "Neutral": (50, "yellow"),
            "Unlucky": (30, "orange"),
            "Very Unlucky": (10, "red"),
        }
        return luck_mapping.get(luck, (50, "grey"))

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Today's Luck")
        st.markdown(f"**Celtic Date:** {celtic_month} {celtic_day}")
        st.markdown(f"**Lunar Phase:** {today_lunar_phase}")
        today_percentage, today_colour = luck_to_bar(today_luck)
        st.progress(today_percentage / 100)
        st.markdown(f"<span style='color:{today_colour}'>{today_luck}</span>", unsafe_allow_html=True)

    with col2:
        st.subheader("Tomorrow's Luck")
        st.markdown(f"**Celtic Date:** {tomorrow_celtic_month} {tomorrow_celtic_day}")
        st.markdown(f"**Lunar Phase:** {tomorrow_lunar_phase}")
        tomorrow_percentage, tomorrow_colour = luck_to_bar(tomorrow_luck)
        st.progress(tomorrow_percentage / 100)
        st.markdown(f"<span style='color:{tomorrow_colour}'>{tomorrow_luck}</span>", unsafe_allow_html=True)
