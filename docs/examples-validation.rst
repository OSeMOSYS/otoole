:orphan:

.. _examples-validation:

-----------------------
Example Validation File
-----------------------

This page holds the datafile used in the validation example. The file can
either be copy/pasted from below, or directly downloaded from :download:`here <_static/validation-data.txt>` ::

    # Model file written by *otoole*
    param default 0 : AccumulatedAnnualDemand :=
    ;
    param default -1 : AnnualEmissionLimit :=
    ;
    param default 0 : AnnualExogenousEmission :=
    ;
    param default 1 : AvailabilityFactor :=
    ;
    param default 1 : CapacityFactor :=
    ;
    param default 0 : CapacityOfOneTechnologyUnit :=
    ;
    param default 1 : CapacityToActivityUnit :=
    R PWRWND 31.536
    R PWRCOA 31.536
    R TRNELC 31.536
    ;
    param default 0 : CapitalCost :=
    R PWRWND 2020 1500
    R PWRWND 2021 1500
    R PWRWND 2022 1500
    R PWRCOA 2020 5000
    R PWRCOA 2021 5000
    R PWRCOA 2022 5000
    ;
    param default 0 : CapitalCostStorage :=
    ;
    param default 0 : Conversionld :=
    ;
    param default 0 : Conversionlh :=
    ;
    param default 0 : Conversionls :=
    ;
    set DAILYTIMEBRACKET :=
    ;
    set DAYTYPE :=
    ;
    param default 0.00137 : DaySplit :=
    ;
    param default 7 : DaysInDayType :=
    ;
    param default 1 : DepreciationMethod :=
    ;
    param default 0.05 : DiscountRate :=
    ;
    param default 0.05 : DiscountRateStorage :=
    ;
    set EMISSION :=
    ;
    param default 0 : EmissionActivityRatio :=
    ;
    param default 0 : EmissionsPenalty :=
    ;
    set FUEL :=
    WND00
    COA00
    ELC01
    ELC02
    ;
    param default 0 : FixedCost :=
    ;
    param default 0 : InputActivityRatio :=
    R PWRWND WND00 1 2020 1
    R PWRWND WND00 1 2021 1
    R PWRWND WND00 1 2022 1
    R PWRCOA COA00 1 2020 1
    R PWRCOA COA00 1 2021 1
    R PWRCOA COA00 1 2022 1
    R TRNELC ELC01 1 2020 1
    R TRNELC ELC01 1 2021 1
    R TRNELC ELC01 1 2022 1
    ;
    set MODE_OF_OPERATION :=
    1
    ;
    param default 0 : MinStorageCharge :=
    ;
    param default -1 : ModelPeriodEmissionLimit :=
    ;
    param default 0 : ModelPeriodExogenousEmission :=
    ;
    param default 1 : OperationalLife :=
    R PWRWND 20
    R PWRCOA 30
    ;
    param default 0 : OperationalLifeStorage :=
    ;
    param default 0 : OutputActivityRatio :=
    R MINWND WND00 1 2020 1
    R MINWND WND00 1 2021 1
    R MINWND WND00 1 2022 1
    R MINCOA COA00 1 2020 1
    R MINCOA COA00 1 2021 1
    R MINCOA COA00 1 2022 1
    R PWRWND ELC01 1 2020 1
    R PWRWND ELC01 1 2021 1
    R PWRWND ELC01 1 2022 1
    R PWRCOA ELC01 1 2020 1
    R PWRCOA ELC01 1 2021 1
    R PWRCOA ELC01 1 2022 1
    R TRNELC ELC02 1 2020 1
    R TRNELC ELC02 1 2021 1
    R TRNELC ELC02 1 2022 1
    ;
    set REGION :=
    R
    ;
    param default 0 : REMinProductionTarget :=
    ;
    param default 0 : RETagFuel :=
    ;
    param default 0 : RETagTechnology :=
    ;
    param default 1 : ReserveMargin :=
    ;
    param default 0 : ReserveMarginTagFuel :=
    ;
    param default 0 : ReserveMarginTagTechnology :=
    ;
    param default 0 : ResidualCapacity :=
    R PWRCOA 2020 0.25
    R PWRCOA 2021 0.25
    R PWRCOA 2022 0.25
    ;
    param default 999 : ResidualStorageCapacity :=
    ;
    set SEASON :=
    ;
    set STORAGE :=
    ;
    param default 0 : SpecifiedAnnualDemand :=
    R ELC02 2020 10
    R ELC02 2021 15
    R ELC02 2022 20
    ;
    param default 0 : SpecifiedDemandProfile :=
    R ELC02 S 2020 0.5
    R ELC02 W 2020 0.5
    R ELC02 S 2021 0.5
    R ELC02 W 2021 0.5
    R ELC02 S 2022 0.5
    R ELC02 W 2022 0.5
    ;
    param default 0 : StorageLevelStart :=
    ;
    param default 0 : StorageMaxChargeRate :=
    ;
    param default 0 : StorageMaxDischargeRate :=
    ;
    set TECHNOLOGY :=
    MINWND
    MINCOA
    PWRWND
    PWRCOA
    TRNELC
    ;
    set TIMESLICE :=
    S
    W
    ;
    param default 0 : TechnologyFromStorage :=
    ;
    param default 0 : TechnologyToStorage :=
    ;
    param default -1 : TotalAnnualMaxCapacity :=
    ;
    param default -1 : TotalAnnualMaxCapacityInvestment :=
    ;
    param default 0 : TotalAnnualMinCapacity :=
    ;
    param default 0 : TotalAnnualMinCapacityInvestment :=
    ;
    param default 0 : TotalTechnologyAnnualActivityLowerLimit :=
    ;
    param default -1 : TotalTechnologyAnnualActivityUpperLimit :=
    ;
    param default 0 : TotalTechnologyModelPeriodActivityLowerLimit :=
    ;
    param default -1 : TotalTechnologyModelPeriodActivityUpperLimit :=
    ;
    param default 0 : TradeRoute :=
    ;
    param default 0 : VariableCost :=
    R MINCOA 1 2020 5
    R MINCOA 1 2021 5
    R MINCOA 1 2022 5
    ;
    set YEAR :=
    2020
    2021
    2022
    ;
    param default 0 : YearSplit :=
    S 2020 0.5
    W 2020 0.5
    S 2021 0.5
    W 2021 0.5
    S 2022 0.5
    W 2022 0.5
    ;
    end;
