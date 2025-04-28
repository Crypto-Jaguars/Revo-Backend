#![no_std]
use soroban_sdk::{contract, contractimpl, contracttype, contracterror, BytesN, String, Address, Env};

#[contracttype]
#[derive(Clone, Debug)]
pub struct CSAMembership {
    pub farm_id: BytesN<32>,
    pub season: String,
    pub share_size: ShareSize,
    pub pickup_location: String,
    pub start_date: u64,
    pub end_date: u64,
    pub member: BytesN<32>,
}

#[contracttype]
#[derive(Clone, Debug)]
pub enum ShareSize {
    Small,
    Medium,
    Large,
    Custom(String),
}

#[contracterror]
#[derive(Clone, Copy, Debug)]
pub enum Error {
    InvalidFarm = 1,
    InvalidDates = 2,
    InvalidSeason = 3,
}

#[contract]
pub struct CSAMembershipContract;

#[contractimpl]
impl CSAMembershipContract {
    pub fn enroll_membership(
        env: Env,
        farm_id: BytesN<32>,
        season: String,
        share_size: ShareSize,
        pickup_location: String,
        start_date: u64,
        end_date: u64,
        member: Address
    ) {
        crate::enroll::enroll_membership(env, farm_id, season, share_size, pickup_location, start_date, end_date, member);
    }

    pub fn update_pickup_location(env: Env, token_id: BytesN<32>, new_location: String, member: Address) {
        crate::manage::update_pickup_location(env, token_id, new_location, member);
    }

    pub fn get_membership_metadata(env: Env, token_id: BytesN<32>) -> Option<CSAMembership> {
        crate::metadata::get_membership_metadata(env, token_id)
    }

    pub fn cancel_membership(env: Env, token_id: BytesN<32>, member: Address) {
        crate::cancel::cancel_membership(env, token_id, member);
    }
}

pub mod enroll;
pub mod manage;
pub mod validate;
pub mod metadata;
pub mod cancel;

#[cfg(test)]
mod test;