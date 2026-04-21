from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

class Perovskite(Base):
    __tablename__ = "perovskites"

    id = Column(Integer, primary_key=True, index=True)
    composition_long_form = Column(String, unique=True, index=True)
    composition_short_form = Column(String, index=True)
    composition_inorganic = Column(Boolean)
    band_gap = Column(Float)
    
    # Sites
    A_1 = Column(String)
    A_1_coef = Column(Float)
    A_2 = Column(String)
    A_2_coef = Column(Float)
    A_3 = Column(String)
    A_3_coef = Column(Float)
    
    B_1 = Column(String)
    B_1_coef = Column(Float)
    
    C_1 = Column(String)
    C_1_coef = Column(Float)
    C_2 = Column(String)
    C_2_coef = Column(Float)
    C_3 = Column(String)
    C_3_coef = Column(Float)
    
    # Physics Descriptors
    r_A = Column(Float)
    en_A = Column(Float)
    mass_A = Column(Float)
    
    r_B = Column(Float)
    en_B = Column(Float)
    mass_B = Column(Float)
    
    r_C = Column(Float)
    en_C = Column(Float)
    mass_C = Column(Float)
    
    tolerance_factor = Column(Float)
    octahedral_factor = Column(Float)

    radius_ratio_ab = Column(Float)
    en_diff_bc = Column(Float)
    mass_ratio_ab = Column(Float)
    
    is_2d = Column(Integer)
    dimension = Column(String, index=True)
    space_group = Column(String, index=True)

    # Relationships
    solar_panels = relationship("SolarPanel", back_populates="perovskite")


class SolarPanel(Base):
    __tablename__ = "solar_panels"

    id = Column(Integer, primary_key=True, index=True)
    data_index = Column(Integer)
    composition_long_form = Column(String, ForeignKey("perovskites.composition_long_form"), index=True)
    
    cell_architecture = Column(String, index=True)
    etl_stack_sequence = Column(String, index=True)
    htl_stack_sequence = Column(String, index=True)
    backcontact_stack_sequence = Column(String)
    backcontact_thickness_list = Column(String)

    jv_default_pce = Column(Float)
    jv_default_voc = Column(Float)
    jv_default_jsc = Column(Float)
    jv_default_ff = Column(Float)
    
    perovskite_band_gap = Column(Float)
    stability_pce_t80 = Column(Float)
    stability_protocol = Column(String, index=True)
    stability_time_total_exposure = Column(Float)
    stability_light_intensity = Column(Float)
    perovskite_annealing_temp = Column(Float)
    perovskite_annealing_time = Column(Float)
    acc_temp = Column(Float)
    acc_humidity = Column(Float)
    cell_area_measured = Column(Float)
    substrate_stack_sequence = Column(String)
    stability_ts80 = Column(Float)
    stability_ts80m = Column(Float)

    # Relationship to Perovskite
    perovskite = relationship("Perovskite", back_populates="solar_panels")
