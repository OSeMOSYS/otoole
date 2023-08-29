\* Problem: OSeMOSYS *\

Minimize
 cost: + TotalDiscountedCost(BB,2016)

Subject To
 EQ_SpecifiedDemand(BB,x,electricity,2016):
 - RateOfDemand(BB,x,electricity,2016) = -2.1101
 CAa1_TotalNewCapacity(BB,gas_import,2016):
 - NewCapacity(BB,gas_import,2016)
 + AccumulatedNewCapacity(BB,gas_import,2016) = -0
 CAa1_TotalNewCapacity(BB,gas_plant,2016):
 - NewCapacity(BB,gas_plant,2016)
 + AccumulatedNewCapacity(BB,gas_plant,2016) = -0
 CAa2_TotalAnnualCapacity(BB,gas_import,2016):
 + AccumulatedNewCapacity(BB,gas_import,2016)
 - TotalCapacityAnnual(BB,gas_import,2016) = -0
 CAa2_TotalAnnualCapacity(BB,gas_plant,2016):
 + AccumulatedNewCapacity(BB,gas_plant,2016)
 - TotalCapacityAnnual(BB,gas_plant,2016) = -3.1101
 CAa3_TotalActivityOfEachTechnology(BB,gas_import,x,2016):
 + RateOfActivity(BB,x,gas_import,1,2016)
 - RateOfTotalActivity(BB,gas_import,x,2016) = -0
 CAa3_TotalActivityOfEachTechnology(BB,gas_plant,x,2016):
 + RateOfActivity(BB,x,gas_plant,1,2016)
 - RateOfTotalActivity(BB,gas_plant,x,2016) = -0
 CAa4_Constraint_Capacity(BB,x,gas_import,2016):
 - TotalCapacityAnnual(BB,gas_import,2016)
 + RateOfTotalActivity(BB,gas_import,x,2016) <= -0
 CAa4_Constraint_Capacity(BB,x,gas_plant,2016):
 - TotalCapacityAnnual(BB,gas_plant,2016)
 + RateOfTotalActivity(BB,gas_plant,x,2016) <= -0
 EBa1_RateOfFuelProduction1(BB,x,natural_gas,gas_import,1,2016):
 + RateOfActivity(BB,x,gas_import,1,2016)
 - RateOfProductionByTechnologyByMode(BB,x,gas_import,1,natural_gas,2016)
 = -0
 EBa1_RateOfFuelProduction1(BB,x,electricity,gas_plant,1,2016):
 + RateOfActivity(BB,x,gas_plant,1,2016)
 - RateOfProductionByTechnologyByMode(BB,x,gas_plant,1,electricity,2016)
 = -0
 EBa2_RateOfFuelProduction2(BB,x,natural_gas,gas_import,2016):
 + RateOfProductionByTechnologyByMode(BB,x,gas_import,1,natural_gas,2016)
 - RateOfProductionByTechnology(BB,x,gas_import,natural_gas,2016) = -0
 EBa2_RateOfFuelProduction2(BB,x,electricity,gas_plant,2016):
 + RateOfProductionByTechnologyByMode(BB,x,gas_plant,1,electricity,2016)
 - RateOfProductionByTechnology(BB,x,gas_plant,electricity,2016) = -0
 EBa3_RateOfFuelProduction3(BB,x,natural_gas,2016):
 + RateOfProductionByTechnology(BB,x,gas_import,natural_gas,2016)
 - RateOfProduction(BB,x,natural_gas,2016) = -0
 EBa3_RateOfFuelProduction3(BB,x,electricity,2016):
 + RateOfProductionByTechnology(BB,x,gas_plant,electricity,2016)
 - RateOfProduction(BB,x,electricity,2016) = -0
 EBa4_RateOfFuelUse1(BB,x,natural_gas,gas_plant,1,2016):
 + 1.1101 RateOfActivity(BB,x,gas_plant,1,2016)
 - RateOfUseByTechnologyByMode(BB,x,gas_plant,1,natural_gas,2016) = -0
 EBa5_RateOfFuelUse2(BB,x,natural_gas,gas_plant,2016):
 + RateOfUseByTechnologyByMode(BB,x,gas_plant,1,natural_gas,2016)
 - RateOfUseByTechnology(BB,x,gas_plant,natural_gas,2016) = -0
 EBa6_RateOfFuelUse3(BB,x,natural_gas,2016):
 + RateOfUseByTechnology(BB,x,gas_plant,natural_gas,2016)
 + RateOfUseByTechnology(BB,x,gas_import,natural_gas,2016)
 - RateOfUse(BB,x,natural_gas,2016) = -0
 EBa7_EnergyBalanceEachTS1(BB,x,natural_gas,2016):
 + RateOfProduction(BB,x,natural_gas,2016)
 - Production(BB,x,natural_gas,2016) = -0
 EBa7_EnergyBalanceEachTS1(BB,x,electricity,2016):
 + RateOfProduction(BB,x,electricity,2016)
 - Production(BB,x,electricity,2016) = -0
 EBa8_EnergyBalanceEachTS2(BB,x,natural_gas,2016):
 + RateOfUse(BB,x,natural_gas,2016) - Use(BB,x,natural_gas,2016) = -0
 EBa9_EnergyBalanceEachTS3(BB,x,electricity,2016):
 + RateOfDemand(BB,x,electricity,2016) - Demand(BB,x,electricity,2016)
 = -0
 EBa11_EnergyBalanceEachTS5(BB,x,natural_gas,2016):
 - Demand(BB,x,natural_gas,2016) + Production(BB,x,natural_gas,2016)
 - Use(BB,x,natural_gas,2016) >= -0
 EBa11_EnergyBalanceEachTS5(BB,x,electricity,2016):
 - Demand(BB,x,electricity,2016) + Production(BB,x,electricity,2016)
 - Use(BB,x,electricity,2016) >= -0
 EBb1_EnergyBalanceEachYear1(BB,natural_gas,2016):
 + Production(BB,x,natural_gas,2016)
 - ProductionAnnual(BB,natural_gas,2016) = -0
 EBb1_EnergyBalanceEachYear1(BB,electricity,2016):
 + Production(BB,x,electricity,2016)
 - ProductionAnnual(BB,electricity,2016) = -0
 EBb2_EnergyBalanceEachYear2(BB,natural_gas,2016):
 + Use(BB,x,natural_gas,2016) - UseAnnual(BB,natural_gas,2016) = -0
 EBb2_EnergyBalanceEachYear2(BB,electricity,2016):
 + Use(BB,x,electricity,2016) - UseAnnual(BB,electricity,2016) = -0
 EBb4_EnergyBalanceEachYear4(BB,natural_gas,2016):
 + ProductionAnnual(BB,natural_gas,2016)
 - UseAnnual(BB,natural_gas,2016) >= -0
 EBb4_EnergyBalanceEachYear4(BB,electricity,2016):
 + ProductionAnnual(BB,electricity,2016)
 - UseAnnual(BB,electricity,2016) >= -0
 Acc1_FuelProductionByTechnology(BB,x,gas_import,natural_gas,2016):
 + RateOfProductionByTechnology(BB,x,gas_import,natural_gas,2016)
 - ProductionByTechnology(BB,x,gas_import,natural_gas,2016) = -0
 Acc1_FuelProductionByTechnology(BB,x,gas_plant,electricity,2016):
 + RateOfProductionByTechnology(BB,x,gas_plant,electricity,2016)
 - ProductionByTechnology(BB,x,gas_plant,electricity,2016) = -0
 Acc2_FuelUseByTechnology(BB,x,gas_plant,natural_gas,2016):
 + RateOfUseByTechnology(BB,x,gas_plant,natural_gas,2016)
 - UseByTechnology(BB,x,gas_plant,natural_gas,2016) = -0
 Acc3_AverageAnnualRateOfActivity(BB,gas_import,1,2016):
 + RateOfActivity(BB,x,gas_import,1,2016)
 - TotalAnnualTechnologyActivityByMode(BB,gas_import,1,2016) = -0
 Acc3_AverageAnnualRateOfActivity(BB,gas_plant,1,2016):
 + RateOfActivity(BB,x,gas_plant,1,2016)
 - TotalAnnualTechnologyActivityByMode(BB,gas_plant,1,2016) = -0
 Acc4_ModelPeriodCostByRegion(BB): + TotalDiscountedCost(BB,2016)
 - ModelPeriodCostByRegion(BB) = -0
 CC1_UndiscountedCapitalInvestment(BB,gas_import,2016):
 + 1e-05 NewCapacity(BB,gas_import,2016)
 - CapitalInvestment(BB,gas_import,2016) = -0
 CC1_UndiscountedCapitalInvestment(BB,gas_plant,2016):
 + 1.03456 NewCapacity(BB,gas_plant,2016)
 - CapitalInvestment(BB,gas_plant,2016) = -0
 CC2_DiscountingCapitalInvestment(BB,gas_import,2016):
 + CapitalInvestment(BB,gas_import,2016)
 - DiscountedCapitalInvestment(BB,gas_import,2016) = -0
 CC2_DiscountingCapitalInvestment(BB,gas_plant,2016):
 + CapitalInvestment(BB,gas_plant,2016)
 - DiscountedCapitalInvestment(BB,gas_plant,2016) = -0
 SV3_SalvageValueAtEndOfPeriod3(BB,gas_import,2016):
 + SalvageValue(BB,gas_import,2016) = -0
 SV3_SalvageValueAtEndOfPeriod3(BB,gas_plant,2016):
 + SalvageValue(BB,gas_plant,2016) = -0
 SV4_SalvageValueDiscountedToStartYear(BB,gas_import,2016):
 - 0.952380952380952 SalvageValue(BB,gas_import,2016)
 + DiscountedSalvageValue(BB,gas_import,2016) = -0
 SV4_SalvageValueDiscountedToStartYear(BB,gas_plant,2016):
 - 0.952380952380952 SalvageValue(BB,gas_plant,2016)
 + DiscountedSalvageValue(BB,gas_plant,2016) = -0
 OC1_OperatingCostsVariable(BB,gas_plant,x,2016):
 + 9.1202 TotalAnnualTechnologyActivityByMode(BB,gas_plant,1,2016)
 - AnnualVariableOperatingCost(BB,gas_plant,2016) = -0
 OC2_OperatingCostsFixedAnnual(BB,gas_import,2016):
 - AnnualFixedOperatingCost(BB,gas_import,2016) = -0
 OC2_OperatingCostsFixedAnnual(BB,gas_plant,2016):
 + 9.1101 TotalCapacityAnnual(BB,gas_plant,2016)
 - AnnualFixedOperatingCost(BB,gas_plant,2016) = -0
 OC3_OperatingCostsTotalAnnual(BB,gas_import,2016):
 - OperatingCost(BB,gas_import,2016)
 + AnnualVariableOperatingCost(BB,gas_import,2016)
 + AnnualFixedOperatingCost(BB,gas_import,2016) = -0
 OC3_OperatingCostsTotalAnnual(BB,gas_plant,2016):
 - OperatingCost(BB,gas_plant,2016)
 + AnnualVariableOperatingCost(BB,gas_plant,2016)
 + AnnualFixedOperatingCost(BB,gas_plant,2016) = -0
 OC4_DiscountedOperatingCostsTotalAnnual(BB,gas_import,2016):
 + 0.975900072948533 OperatingCost(BB,gas_import,2016)
 - DiscountedOperatingCost(BB,gas_import,2016) = -0
 OC4_DiscountedOperatingCostsTotalAnnual(BB,gas_plant,2016):
 + 0.975900072948533 OperatingCost(BB,gas_plant,2016)
 - DiscountedOperatingCost(BB,gas_plant,2016) = -0
 TDC1_TotalDiscountedCostByTechnology(BB,gas_import,2016):
 + DiscountedCapitalInvestment(BB,gas_import,2016)
 - DiscountedSalvageValue(BB,gas_import,2016)
 + DiscountedOperatingCost(BB,gas_import,2016)
 - TotalDiscountedCostByTechnology(BB,gas_import,2016)
 + DiscountedTechnologyEmissionsPenalty(BB,gas_import,2016) = -0
 TDC1_TotalDiscountedCostByTechnology(BB,gas_plant,2016):
 + DiscountedCapitalInvestment(BB,gas_plant,2016)
 - DiscountedSalvageValue(BB,gas_plant,2016)
 + DiscountedOperatingCost(BB,gas_plant,2016)
 - TotalDiscountedCostByTechnology(BB,gas_plant,2016)
 + DiscountedTechnologyEmissionsPenalty(BB,gas_plant,2016) = -0
 TDC2_TotalDiscountedCost(BB,2016):
 + TotalDiscountedCostByTechnology(BB,gas_import,2016)
 + TotalDiscountedCostByTechnology(BB,gas_plant,2016)
 - TotalDiscountedCost(BB,2016) = -0
 AAC1_TotalAnnualTechnologyActivity(BB,gas_import,2016):
 + RateOfTotalActivity(BB,gas_import,x,2016)
 - TotalTechnologyAnnualActivity(BB,gas_import,2016) = -0
 AAC1_TotalAnnualTechnologyActivity(BB,gas_plant,2016):
 + RateOfTotalActivity(BB,gas_plant,x,2016)
 - TotalTechnologyAnnualActivity(BB,gas_plant,2016) = -0
 TAC1_TotalModelHorizonTechnologyActivity(BB,gas_import):
 + TotalTechnologyAnnualActivity(BB,gas_import,2016)
 - TotalTechnologyModelPeriodActivity(BB,gas_import) = -0
 TAC1_TotalModelHorizonTechnologyActivity(BB,gas_plant):
 + TotalTechnologyAnnualActivity(BB,gas_plant,2016)
 - TotalTechnologyModelPeriodActivity(BB,gas_plant) = -0
 RM1_ReserveMargin_TechnologiesIncluded_In_Activity_Units(BB,x,2016):
 - TotalCapacityInReserveMargin(BB,2016) = -0
 RM2_ReserveMargin_FuelsIncluded(BB,x,2016):
 - DemandNeedingReserveMargin(BB,x,2016) = -0
 RM3_ReserveMargin_Constraint(BB,x,2016):
 - TotalCapacityInReserveMargin(BB,2016)
 + DemandNeedingReserveMargin(BB,x,2016) <= -0
 RE1_FuelProductionByTechnologyAnnual(BB,gas_import,natural_gas,2016):
 + ProductionByTechnology(BB,x,gas_import,natural_gas,2016)
 - ProductionByTechnologyAnnual(BB,gas_import,natural_gas,2016) = -0
 RE1_FuelProductionByTechnologyAnnual(BB,gas_plant,electricity,2016):
 + ProductionByTechnology(BB,x,gas_plant,electricity,2016)
 - ProductionByTechnologyAnnual(BB,gas_plant,electricity,2016) = -0
 RE2_TechIncluded(BB,2016): - TotalREProductionAnnual(BB,2016) = -0
 RE3_FuelIncluded(BB,2016):
 - RETotalProductionOfTargetFuelAnnual(BB,2016) = -0
 RE4_EnergyConstraint(BB,2016): - TotalREProductionAnnual(BB,2016) <= -0
 RE5_FuelUseByTechnologyAnnual(BB,gas_plant,natural_gas,2016):
 + RateOfUseByTechnology(BB,x,gas_plant,natural_gas,2016)
 - UseByTechnologyAnnual(BB,gas_plant,natural_gas,2016) = -0
 E4_EmissionsPenaltyByTechnology(BB,gas_import,2016):
 - AnnualTechnologyEmissionsPenalty(BB,gas_import,2016) = -0
 E4_EmissionsPenaltyByTechnology(BB,gas_plant,2016):
 - AnnualTechnologyEmissionsPenalty(BB,gas_plant,2016) = -0
 E5_DiscountedEmissionsPenaltyByTechnology(BB,gas_import,2016):
 + 0.975900072948533 AnnualTechnologyEmissionsPenalty(BB,gas_import,2016)
 - DiscountedTechnologyEmissionsPenalty(BB,gas_import,2016) = -0
 E5_DiscountedEmissionsPenaltyByTechnology(BB,gas_plant,2016):
 + 0.975900072948533 AnnualTechnologyEmissionsPenalty(BB,gas_plant,2016)
 - DiscountedTechnologyEmissionsPenalty(BB,gas_plant,2016) = -0

Bounds
 TotalTechnologyModelPeriodActivity(BB,gas_import) free
 TotalTechnologyModelPeriodActivity(BB,gas_plant) free
 TotalREProductionAnnual(BB,2016) free
 RETotalProductionOfTargetFuelAnnual(BB,2016) free

End
