use soroban_sdk::{Env, BytesN, String, panic_with_error};
use crate::Error;

pub fn validate_season(env: &Env, farm_id: BytesN<32>, season: String, start_date: u64, end_date: u64) {
    if !is_farm_registered(env, &farm_id) {
        panic_with_error!(env, Error::InvalidFarm);
    }

    if start_date >= end_date || start_date < env.ledger().timestamp() {
        panic_with_error!(env, Error::InvalidDates);
    }

    if season.len() == 0 || season.len() > 32 {
        panic_with_error!(env, Error::InvalidSeason);
    }
}

fn is_farm_registered(_env: &Env, _farm_id: &BytesN<32>) -> bool {
    true // Simulación, reemplazar con lógica real
}