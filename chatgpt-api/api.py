# app.py

from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# an map of urls
urls = {
    "AELF.explorer": "https://explorer.aelf.io/api",
    "AELF.api": "https://aelf-public-node.aelf.io/api",
    "tDVV.explorer": "https://tdvv-explorer.aelf.io/api",
    "tDVV.api": "https://tdvv-public-node.aelf.io/api",
    "cmc": "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"
}

CMC_API_KEY = "8241d5b8-e357-4ccc-a7ed-124e97c477b3"

def extract_pure_address(address):
    # Remove 'ELF_' prefix if present
    if address.startswith('ELF_'):
        address = address[4:]
    
    # Find the first underscore position
    first_underscore = address.find('_')
    
    # If an underscore is found, remove everything from it onwards
    if first_underscore != -1:
        address = address[:first_underscore]
    
    return address
    
def get_chain_api_url(chain_id):
    if chain_id == 'AELF':
        return urls['AELF.api']
    elif chain_id == 'tDVV':
        return urls['tDVV.api']
    else:
        return None
    
def get_chain_explorer_url(chain_id):
    if chain_id == 'AELF':
        return urls['AELF.explorer']
    elif chain_id == 'tDVV':
        return urls['tDVV.explorer']
    else:
        return None
    
@app.route('/get-chains', methods=['GET'])
def get_chains():
    # Return the list of supported chains
    return jsonify({
        'chains': ['AELF', 'tDVV']
    })

@app.route('/get-balance', methods=['GET'])
def get_balance():
    address = request.args.get('address', type=str)
    chain_id = request.args.get('chainId', default='AELF', type=str)

    if not chain_id:
        return jsonify({
            'error': 'Valid chainId parameter is required'
        }), 400
    
    chainUrl = get_chain_explorer_url(chain_id)

    if(chainUrl == None):
        return jsonify({
            'error': 'Invalid chainId'
        }), 400

    if not address:
        return jsonify({
            'error': 'Address parameter is required'
        }), 400

    params = {
        'address': extract_pure_address(address)
    }

    response = requests.get(chainUrl + '/viewer/balances', params=params)

    if response.status_code == 200:
        return jsonify(response.json())
    else:
        return jsonify({
            'error': 'Failed to fetch data'
        }), response.status_code

@app.route('/get-price', methods=['GET'])
def get_price():
    symbol = request.args.get('symbol', default='ELF', type=str)
    
    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': CMC_API_KEY,
    }

    params = {
        'symbol': symbol
    }

    response = requests.get(urls['cmc'], headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()
        if symbol in data['data']:
            price = data['data'][symbol]['quote']['USD']['price']
            return jsonify({
                'symbol': symbol,
                'price': price
            })
        else:
            return jsonify({
                'error': 'Token not found'
            }), 404
    else:
        return jsonify({
            'error': 'Failed to fetch data'
        }), response.status_code
    
@app.route('/get-transaction-result', methods=['GET'])
def get_transaction_result():
    tx_id = request.args.get('transactionId', type=str)
    chain_id = request.args.get('chainId', default='AELF', type=str)

    if not tx_id:
        return jsonify({
            'error': 'transactionId parameter is required'
        }), 400
    
    if not chain_id:
        return jsonify({
            'error': 'Valid chainId parameter is required'
        }), 400

    params = {
        'transactionId': tx_id
    }


    chainUrl = get_chain_api_url(chain_id)

    if(chainUrl == None):
        return jsonify({
            'error': 'Invalid chainId'
        }), 400

    response = requests.get(chainUrl + '/blockChain/transactionResult', params=params)

    if response.status_code == 200:
        return jsonify(response.json())
    else:
        return jsonify({
            'error': 'Failed to fetch data'
        }), response.status_code
    
@app.route('/get-block-height', methods=['GET'])
def get_block_height():
    chain_id = request.args.get('chainId', default='AELF', type=str)

    if not chain_id:
        return jsonify({
            'error': 'Valid chainId parameter is required'
        }), 400
    
    chainUrl = get_chain_api_url(chain_id)

    if(chainUrl == None):
        return jsonify({
            'error': 'Invalid chainId'
        }), 400
    
    response = requests.get(chainUrl + '/blockChain/blockHeight')

    if response.status_code == 200:
        return jsonify(response.json())
    else:
        return jsonify({
            'error': 'Failed to fetch data'
        }), response.status_code
    
@app.route('/block-by-height', methods=['GET'])
def get_block_by_height():
    block_height = request.args.get('blockHeight', type=int)
    include_txs = request.args.get('includeTransactions', default=False, type=bool)
    chain_id = request.args.get('chainId', default='AELF', type=str)

    if not chain_id:
        return jsonify({
            'error': 'Valid chainId parameter is required'
        }), 400
    
    chainUrl = get_chain_api_url(chain_id)

    if(chainUrl == None):
        return jsonify({
            'error': 'Invalid chainId'
        }), 400

    if block_height is None:
        return jsonify({
            'error': 'blockHeight parameter is required'
        }), 400

    params = {
        'blockHeight': block_height,
        'includeTransactions': include_txs
    }

    response = requests.get(chainUrl + '/blockChain/blockByHeight', params=params)

    if response.status_code == 200:
        return jsonify(response.json())
    else:
        return jsonify({
            'error': 'Failed to fetch data'
        }), response.status_code
    
@app.route('/get-transactions-by-address', methods=['GET'])
def get_transactions_by_address():
    address = request.args.get('address', type=str)
    page = request.args.get('page', default=0, type=int)
    limit = request.args.get('limit', default=10, type=int)
    chain_id = request.args.get('chainId', default='AELF', type=str)

    if not chain_id:
        return jsonify({
            'error': 'Valid chainId parameter is required'
        }), 400
    
    chainUrl = get_chain_explorer_url(chain_id)

    if(chainUrl == None):
        return jsonify({
            'error': 'Invalid chainId'
        }), 400

    if not address:
        return jsonify({
            'error': 'address parameter is required'
        }), 400

    params = {
        'address': extract_pure_address(address),
        'page': page,
        'limit': limit
    }

    response = requests.get(chainUrl + '/address/transactions', params=params)

    if response.status_code == 200:
        return jsonify(response.json())
    else:
        return jsonify({
            'error': 'Failed to fetch data'
        }), response.status_code

if __name__ == '__main__':
    app.run(debug=True)