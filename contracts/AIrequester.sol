// SPDX-License-Identifier: MIT
pragma solidity >=0.7.0 <0.9.0;

import "@chainlink/contracts/src/v0.8/ChainlinkClient.sol";
import "@chainlink/contracts/src/v0.8/ConfirmedOwner.sol";

//Starter code for oracle to request AI to run 
//Still has a bunch of values to change and figure out

/**
 * Request testnet LINK and ETH here: https://faucets.chain.link/
 * Find information on LINK Token Contracts and get the latest ETH and LINK faucets here: https://docs.chain.link/docs/link-token-contracts/
 */

/**
 * THIS IS AN EXAMPLE CONTRACT WHICH USES HARDCODED VALUES FOR CLARITY.
 * THIS EXAMPLE USES UN-AUDITED CODE.
 * DO NOT USE THIS CODE IN PRODUCTION.
 */

contract AIrequester is ChainlinkClient, ConfirmedOwner {
    using Chainlink for Chainlink.Request;

    //output type still has to be determined
    string public output;
    bytes32 private jobId;
    uint256 private fee;

    event RequestAI(bytes32 indexed requestId, string output);

    /**
     * @notice Initialize the link token and target oracle
     *
     * Sepolia Testnet details:
     * Link Token: (Link Token Address)
     * Oracle: (Oracle Address) (Chainlink DevRel)
     * jobId: (jobId) e.g.  ca98366cc7314957b8c012c72f05aeeb
     * 
     */

    constructor() ConfirmedOwner(msg.sender) {
        setChainlinkToken(/*Link Token Address*/);
        setChainlinkOracle(/*Oracle Address*/);
        jobId = /*jobId*/; 
        fee = (1 * LINK_DIVISIBILITY) / 10; // 0,1 * 10**18 (Varies by network and job)
    }

    /**
     * Create a Chainlink request to retrieve API response, find the target
     */
    function RequestAIData() public returns (bytes32 requestId) {
        Chainlink.Request memory req = buildChainlinkRequest(
            jobId,
            address(this),
            this.fulfill.selector
        );

        // Set the URL to perform the GET request on
        req.add(
            "get",
            url //has to be determined
        );

        // Set the path to find the desired data in the API response, 
        req.add("path", path); //path has to be determined

        // Sends the request
        return sendChainlinkRequest(req, fee);
    }

    /**
     * Receive the response in the form of a string
     */
    function fulfill(
        bytes32 _requestId,
        string _output //not sure how the output will be might need change
    ) public recordChainlinkFulfillment(_requestId) {
        emit RequestAI(_requestId, _output);
        output = _ouput;
    }

    /**
     * Allow withdraw of Link tokens from the contract
     */
    function withdrawLink() public onlyOwner {
        LinkTokenInterface link = LinkTokenInterface(chainlinkTokenAddress());
        require(
            link.transfer(msg.sender, link.balanceOf(address(this))),
            "Unable to transfer"
        );
    }
}