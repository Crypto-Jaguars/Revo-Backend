use soroban_sdk::{Address, Env, BytesN, xdr::ToXdr};
use crate::CSAMembership;

pub fn cancel_membership(env: Env, token_id: BytesN<32>, member: Address) {
    member.require_auth();
    let membership: CSAMembership = env.storage().persistent().get(&token_id)
        .expect("Membership not found");

    let member_xdr = member.clone().to_xdr(&env); // Usar clone para evitar mover member
    let mut member_array = [0u8; 32];
    member_xdr.copy_into_slice(&mut member_array);
    let member_bytesn = BytesN::from_array(&env, &member_array);

    if membership.member != member_bytesn {
        panic!("Unauthorized");
    }

    env.storage().persistent().remove(&token_id);
    env.events().publish(("cancel_membership", "success"), (&member, &token_id));
}