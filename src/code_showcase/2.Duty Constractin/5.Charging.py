{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "d1be8975-a287-405f-bd34-034e22e39575",
   "metadata": {},
   "outputs": [],
   "source": [
    "from typing import Dict, List, Tuple\n",
    "from .types import DwellEvent, EnergyConfig, MergeCandidate\n",
    "\n",
    "\n",
    "def schedule_charging_dwells(\n",
    "    duties: List[List[int]],\n",
    "    merge_info: Dict[Tuple[int, int], MergeCandidate],\n",
    "    config: EnergyConfig,\n",
    ") -> List[DwellEvent]:\n",
    "    \"\"\"\n",
    "    Simplified depot-dwell scheduler.\n",
    "\n",
    "    For each selected block merge i -> j, schedule charging immediately\n",
    "    after arriving at the depot, if enough time is available.\n",
    "    \"\"\"\n",
    "\n",
    "    events: List[DwellEvent] = []\n",
    "    wh_per_minute = config.charge_rate_wh_per_hour / 60.0\n",
    "\n",
    "    for duty in duties:\n",
    "        for i, j in zip(duty, duty[1:]):\n",
    "            candidate = merge_info.get((i, j))\n",
    "\n",
    "            if candidate is None:\n",
    "                continue\n",
    "\n",
    "            start = candidate.arrive_depot_time\n",
    "            end = start + candidate.required_charge_minutes * 60\n",
    "\n",
    "            if end > candidate.latest_depart_time:\n",
    "                continue\n",
    "\n",
    "            start_energy = 0.0\n",
    "            charged_energy = candidate.required_charge_minutes * wh_per_minute\n",
    "            end_energy = min(config.battery_capacity, start_energy + charged_energy)\n",
    "\n",
    "            events.append(\n",
    "                DwellEvent(\n",
    "                    from_block=i,\n",
    "                    to_block=j,\n",
    "                    depot_id=candidate.depot_id,\n",
    "                    start_time=start,\n",
    "                    end_time=end,\n",
    "                    start_energy=start_energy,\n",
    "                    end_energy=end_energy,\n",
    "                )\n",
    "            )\n",
    "\n",
    "    return events"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3 (ipykernel)",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.13.12"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}
