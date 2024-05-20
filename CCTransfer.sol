// SPDX-License-Identifier: AGPL-3.0-or-later
pragma solidity ^0.8.18;

interface CoinLike {
    function mint(address usr, uint wad) external;
    function burn(address usr, uint wad) external;
    function transfer(address,uint256) external;
    function transferFrom(address,address,uint256) external;
}

interface RelayLike {
    function isApproved(address,uint) external view returns (bool);
}

contract CCTransfer {

    struct Request { 
        bool incoming;
        uint256 amount;
        address sender;
        string target_chain; // change this if appropriate
        address target_account;  //change this if appropriate
    }

    mapping (uint => uint) aborted;
    Request[] requests;
    CoinLike coin;
    RelayLike relay;

    constructor (address coin_, address relay_) {
        coin = CoinLike(coin_);
        relay = RelayLike(relay_);
    }

    function addIncomingRequest(uint256 amount, address target_account) external { // change the parameter types if appropriate
        requests.push(Request(true, amount, address(this), "", target_account));
    }

    function addOutgoingRequest(uint256 amount, string calldata target_chain, address target_account) external { // change the parameter types if appropriate
        coin.transferFrom(msg.sender, address(this), amount);
        requests.push(Request(false, amount, msg.sender, target_chain, target_account));
    }

    function abortRequest(uint index) external {
        require(msg.sender == requests[index].sender);
        coin.transfer(msg.sender, requests[index].amount);
    }

    function commitRequest(uint index) external {
        bool approved = relay.isApproved(address(this), index);
        require(approved, "Multi-Dai-CCTransfer/not-approved-0");
        if (requests[index].incoming) {
            coin.mint(requests[index].target_account, requests[index].amount);
        } else {
            coin.burn(address(this), requests[index].amount);
        }
    }

    function getNumberOfRequests() external view returns (uint) {
        return requests.length;
    }

}