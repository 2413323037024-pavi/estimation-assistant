
import math
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="AI Home Building Assistant",
    page_icon="🏠",
    layout="wide"
)

st.title("🏠 AI Home Building Assistant")
st.caption("Building details • Material estimation • Approximate cost report")

st.info(
    "This is a prototype for preliminary estimation. "
    "It is not a substitute for an engineer's structural design or BOQ."
)

# --------------------------------------------------
# STEP 1: BUILDING DETAILS
# --------------------------------------------------

st.header("1. Building Details")

c1, c2 = st.columns(2)

with c1:
    project_name = st.text_input(
        "Project Name",
        "My Home Construction"
    )

    construction_type = st.selectbox(
        "Construction Type",
        [
            "Individual House",
            "Duplex / Double-Storey House",
            "Apartment Building",
            "Commercial Building",
            "Custom Construction"
        ]
    )

    construction_stage = st.selectbox(
        "Construction Stage",
        [
            "New Construction",
            "Renovation",
            "Extension / Additional Floor"
        ]
    )

with c2:
    structural_type = st.selectbox(
        "Structural Type",
        [
            "RCC Framed Structure",
            "Load-Bearing Structure",
            "Steel Structure",
            "Composite Structure",
            "Not Decided"
        ]
    )

    floors = st.number_input(
        "Number of Floors",
        min_value=1,
        max_value=50,
        value=1,
        step=1
    )

    floor_height = st.number_input(
        "Floor Height (metres)",
        min_value=2.0,
        max_value=6.0,
        value=3.0,
        step=0.1
    )

# --------------------------------------------------
# STEP 2: AREA AND ROOM DETAILS
# --------------------------------------------------

st.header("2. Area and Room Details")

c1, c2, c3 = st.columns(3)

with c1:
    plot_area = st.number_input(
        "Plot Area (sq.ft)",
        min_value=0.0,
        value=1200.0,
        step=50.0
    )

with c2:
    area_per_floor = st.number_input(
        "Built-up Area per Floor (sq.ft)",
        min_value=0.0,
        value=900.0,
        step=50.0
    )

with c3:
    total_builtup_area = area_per_floor * floors
    st.metric(
        "Total Built-up Area",
        f"{total_builtup_area:,.2f} sq.ft"
    )

if plot_area > 0 and area_per_floor > plot_area:
    st.warning(
        "Built-up area per floor exceeds plot area. "
        "Please verify the inputs."
    )

st.subheader("Room-wise Dimensions")

default_rooms = pd.DataFrame({
    "Room": [
        "Living Room",
        "Bedroom 1",
        "Bedroom 2",
        "Kitchen",
        "Bathroom"
    ],
    "Length (ft)": [15.0, 12.0, 12.0, 10.0, 7.0],
    "Width (ft)": [12.0, 10.0, 10.0, 8.0, 5.0],
    "Quantity": [1, 1, 1, 1, 1]
})

rooms = st.data_editor(
    default_rooms,
    num_rows="dynamic",
    use_container_width=True,
    key="room_details",
    column_config={
        "Room": st.column_config.TextColumn(
            "Room Name",
            required=True
        ),
        "Length (ft)": st.column_config.NumberColumn(
            min_value=0.0,
            step=1.0
        ),
        "Width (ft)": st.column_config.NumberColumn(
            min_value=0.0,
            step=1.0
        ),
        "Quantity": st.column_config.NumberColumn(
            min_value=1,
            step=1
        )
    }
)

# --------------------------------------------------
# STEP 3: ESTIMATION SETTINGS AND MATERIAL RATES
# --------------------------------------------------

st.header("3. Estimation Settings")

c1, c2, c3 = st.columns(3)

with c1:
    tile_wastage = st.number_input(
        "Tile Wastage (%)",
        min_value=0.0,
        max_value=30.0,
        value=10.0
    )

    wall_openings = st.slider(
        "Wall Area Deduction for Doors/Windows (%)",
        min_value=0,
        max_value=50,
        value=15
    )

with c2:
    paint_coats = st.number_input(
        "Number of Paint Coats",
        min_value=1,
        max_value=5,
        value=2
    )

    paint_coverage = st.number_input(
        "Paint Coverage (sq.ft/litre/coat)",
        min_value=10.0,
        value=100.0,
        step=5.0
    )

with c3:
    slab_thickness = st.number_input(
        "Indicative Slab Thickness (inches)",
        min_value=1.0,
        max_value=24.0,
        value=5.0,
        step=0.5
    )

st.subheader("Material Rates (₹)")

st.caption(
    "Enter local supplier rates. These are example starting values, "
    "not verified current market prices."
)

rate_cols = st.columns(3)

with rate_cols[0]:
    tile_rate = st.number_input(
        "Floor Tiles (₹/sq.ft)",
        min_value=0.0,
        value=60.0
    )

    paint_rate = st.number_input(
        "Paint (₹/litre)",
        min_value=0.0,
        value=300.0
    )

with rate_cols[1]:
    cement_rate = st.number_input(
        "Cement (₹/50 kg bag)",
        min_value=0.0,
        value=400.0
    )

    sand_rate = st.number_input(
        "Sand (₹/cu.ft)",
        min_value=0.0,
        value=80.0
    )

with rate_cols[2]:
    aggregate_rate = st.number_input(
        "Aggregate (₹/cu.ft)",
        min_value=0.0,
        value=70.0
    )

    labour_cost = st.number_input(
        "Additional Labour Budget (₹)",
        min_value=0.0,
        value=0.0,
        step=5000.0
    )

# --------------------------------------------------
# STEP 4: CALCULATE ESTIMATES
# --------------------------------------------------

st.header("4. Calculate Estimate")

if st.button("Calculate Material Estimate", type="primary"):

    if area_per_floor <= 0:
        st.error("Built-up area must be greater than zero.")

    elif not rooms.empty and (
        (rooms["Length (ft)"] <= 0).any()
        or (rooms["Width (ft)"] <= 0).any()
        or (rooms["Quantity"] < 1).any()
    ):
        st.error(
            "Please enter valid positive room dimensions and quantities."
        )

    else:
        # Room floor areas
        if rooms.empty:
            room_floor_area = 0.0
            room_wall_area = 0.0
        else:
            room_floor_area = (
                rooms["Length (ft)"]
                * rooms["Width (ft)"]
                * rooms["Quantity"]
            ).sum()

            room_perimeter = 2 * (
                rooms["Length (ft)"] + rooms["Width (ft)"]
            )

            room_wall_area = (
                room_perimeter
                * floor_height
                * rooms["Quantity"]
            ).sum()

        # Use entered built-up area for overall floor quantity.
        # Room dimensions are used for room-based wall calculations.
        tile_area = total_builtup_area
        tile_quantity = tile_area * (1 + tile_wastage / 100)

        # Approximate internal wall paint area.
        net_wall_area = room_wall_area * (
            1 - wall_openings / 100
        )

        paint_quantity = (
            net_wall_area * paint_coats / paint_coverage
        ) if paint_coverage > 0 else 0

        # Indicative slab volume only; not structural design.
        slab_thickness_m = slab_thickness * 0.0254
        slab_area_m2 = total_builtup_area * 0.092903
        slab_volume_m3 = slab_area_m2 * slab_thickness_m

        # Indicative concrete material split using 1:2:4.
        # Dry volume factor is an approximate allowance.
        dry_concrete_m3 = slab_volume_m3 * 1.54
        mix_total = 1 + 2 + 4

        cement_m3 = dry_concrete_m3 * (1 / mix_total)
        sand_m3 = dry_concrete_m3 * (2 / mix_total)
        aggregate_m3 = dry_concrete_m3 * (4 / mix_total)

        cement_bags = (cement_m3 * 1440) / 50
        sand_cuft = sand_m3 * 35.3147
        aggregate_cuft = aggregate_m3 * 35.3147

        # Approximate material costs
        tile_cost = tile_quantity * tile_rate
        paint_cost = paint_quantity * paint_rate
        cement_cost = cement_bags * cement_rate
        sand_cost = sand_cuft * sand_rate
        aggregate_cost = aggregate_cuft * aggregate_rate

        estimate_rows = [
            {
                "Material / Item": "Floor Tiles",
                "Estimated Quantity": round(tile_quantity, 2),
                "Unit": "sq.ft",
                "Rate (₹)": tile_rate,
                "Estimated Cost (₹)": round(tile_cost, 2)
            },
            {
                "Material / Item": "Paint",
                "Estimated Quantity": round(paint_quantity, 2),
                "Unit": "litres",
                "Rate (₹)": paint_rate,
                "Estimated Cost (₹)": round(paint_cost, 2)
            },
            {
                "Material / Item": "Cement for Indicative Slab Mix",
                "Estimated Quantity": round(cement_bags, 2),
                "Unit": "50 kg bags",
                "Rate (₹)": cement_rate,
                "Estimated Cost (₹)": round(cement_cost, 2)
            },
            {
                "Material / Item": "Sand for Indicative Slab Mix",
                "Estimated Quantity": round(sand_cuft, 2),
                "Unit": "cu.ft",
                "Rate (₹)": sand_rate,
                "Estimated Cost (₹)": round(sand_cost, 2)
            },
            {
                "Material / Item": "Aggregate for Indicative Slab Mix",
                "Estimated Quantity": round(aggregate_cuft, 2),
                "Unit": "cu.ft",
                "Rate (₹)": aggregate_rate,
                "Estimated Cost (₹)": round(aggregate_cost, 2)
            },
            {
                "Material / Item": "Additional Labour Budget",
                "Estimated Quantity": 1,
                "Unit": "budget",
                "Rate (₹)": labour_cost,
                "Estimated Cost (₹)": labour_cost
            }
        ]

        estimate_df = pd.DataFrame(estimate_rows)
        material_total = estimate_df["Estimated Cost (₹)"].sum()

        # Save results in session state so the report remains visible
        st.session_state["estimate_df"] = estimate_df
        st.session_state["estimate_total"] = material_total
        st.session_state["estimate_project"] = project_name
        st.session_state["estimate_type"] = construction_type
        st.session_state["estimate_stage"] = construction_stage
        st.session_state["estimate_structure"] = structural_type
        st.session_state["estimate_floors"] = floors
        st.session_state["estimate_area"] = total_builtup_area
        st.session_state["estimate_room_area"] = room_floor_area
        st.session_state["estimate_wall_area"] = net_wall_area
        st.session_state["estimate_slab_volume"] = slab_volume_m3

# --------------------------------------------------
# STEP 5: ESTIMATION REPORT
# --------------------------------------------------

if "estimate_df" in st.session_state:

    st.header("5. Estimation Report")

    m1, m2, m3 = st.columns(3)

    m1.metric(
        "Total Built-up Area",
        f"{st.session_state['estimate_area']:,.2f} sq.ft"
    )

    m2.metric(
        "Indicative Slab Volume",
        f"{st.session_state['estimate_slab_volume']:.2f} m³"
    )

    m3.metric(
        "Included Item Cost Total",
        f"₹{st.session_state['estimate_total']:,.2f}"
    )

    st.subheader("Project Summary")

    st.write(f"**Project:** {st.session_state['estimate_project']}")
    st.write(f"**Construction Type:** {st.session_state['estimate_type']}")
    st.write(f"**Construction Stage:** {st.session_state['estimate_stage']}")
    st.write(f"**Structural Type:** {st.session_state['estimate_structure']}")
    st.write(f"**Number of Floors:** {st.session_state['estimate_floors']}")

    st.subheader("Material Quantity and Cost Table")

    st.dataframe(
        st.session_state["estimate_df"],
        use_container_width=True,
        hide_index=True
    )

    csv_data = st.session_state["estimate_df"].to_csv(
        index=False
    ).encode("utf-8-sig")

    st.download_button(
        "Download Estimate as CSV",
        data=csv_data,
        file_name="home_building_estimate.csv",
        mime="text/csv"
    )

    st.warning(
        "This preliminary report does not include a complete BOQ, "
        "foundation, columns, beams, reinforcement design, brickwork, "
        "plaster, plumbing, electrical work, waterproofing, approvals, "
        "taxes or all labour costs. The slab mix is only an illustrative "
        "quantity calculation and must not be used as a structural design."
    )

st.divider()
st.caption(
    "AI Home Building Assistant | Prototype for learning and estimation"
)
